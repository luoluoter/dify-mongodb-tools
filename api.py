"""
API路由模块
定义所有API端点的路由处理逻辑
"""

import logging
from typing import Dict, Any
from flask import Blueprint, request, jsonify
from pymongo.errors import PyMongoError

from database import MongoDBManager

logger = logging.getLogger(__name__)

# 创建蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')


def get_db_manager() -> MongoDBManager:
    """
    获取数据库管理器实例
    
    Returns:
        MongoDBManager: 数据库管理器实例
    """
    from app import get_db_manager
    return get_db_manager()


@api_bp.route("/save", methods=["POST"])
def save_data():
    """
    保存数据到指定的数据库和集合
    
    支持写入任意结构的数据，content字段必须是JSON字符串，
    会自动解析成object存入data字段。必须指定目标数据库和集合。
    
    Returns:
        JSON响应: 包含操作结果和ID
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "请求体不能为空"}), 400
        
        # 验证必需参数
        if not data.get("db_name"):
            return jsonify({"error": "必须指定 db_name 参数"}), 400
        if not data.get("collection_name"):
            return jsonify({"error": "必须指定 collection_name 参数"}), 400
        
        db_manager = get_db_manager()
        result = db_manager.save_data(data)
        
        # 检查是否有错误
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result), 200
        
    except PyMongoError as e:
        logger.error(f"数据库操作失败: {e}")
        return jsonify({"error": "数据库操作失败"}), 500
    except Exception as e:
        logger.error(f"保存数据时发生错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


@api_bp.route("/search", methods=["GET"])
def search_data():
    """
    搜索数据
    
    支持复杂的查询条件、排序和分页，必须指定目标数据库和集合
    
    Query Parameters:
        db_name: 数据库名称（必需）
        collection_name: 集合名称（必需）
        uuid_name: UUID字段名（可选，默认为uuid）
        uuid: UUID值（可选）
        conditions: 查询条件JSON字符串（可选）
        sorts: 排序条件JSON字符串（可选）
        limit: 限制返回数量（可选，默认5）
        skip: 跳过数量（可选，默认0）
    
    Returns:
        JSON响应: 查询结果列表
    """
    try:
        query_params = request.args.to_dict()
        
        # 验证必需参数
        if not query_params.get("db_name"):
            return jsonify({"error": "必须指定 db_name 参数"}), 400
        if not query_params.get("collection_name"):
            return jsonify({"error": "必须指定 collection_name 参数"}), 400
        
        db_manager = get_db_manager()
        results = db_manager.search_data(query_params)
        
        return jsonify(results), 200
        
    except PyMongoError as e:
        logger.error(f"数据库查询失败: {e}")
        return jsonify({"error": "数据库查询失败"}), 500
    except Exception as e:
        logger.error(f"搜索数据时发生错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


@api_bp.route("/health", methods=["GET"])
def health_check():
    """
    健康检查端点
    
    Returns:
        JSON响应: 服务状态信息
    """
    try:
        db_manager = get_db_manager()
        # 尝试连接数据库
        db_manager.client.admin.command('ping')
        
        return jsonify({
            "status": "healthy",
            "message": "服务运行正常",
            "database": "connected"
        }), 200
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return jsonify({
            "status": "unhealthy",
            "message": "服务异常",
            "database": "disconnected",
            "error": str(e)
        }), 503


@api_bp.errorhandler(404)
def not_found(error):
    """处理404错误"""
    return jsonify({"error": "接口不存在"}), 404


@api_bp.errorhandler(405)
def method_not_allowed(error):
    """处理405错误"""
    return jsonify({"error": "请求方法不允许"}), 405


@api_bp.errorhandler(500)
def internal_error(error):
    """处理500错误"""
    logger.error(f"服务器内部错误: {error}")
    return jsonify({"error": "服务器内部错误"}), 500 