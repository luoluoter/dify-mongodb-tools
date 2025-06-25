"""
Dify MongoDB Tools - 主应用模块

一个用于与MongoDB交互的Flask应用，提供数据写入和查询功能。
支持Dify工具集集成。

主要功能:
- 数据保存到指定数据库和集合 (/api/save)
- 数据搜索和查询 (/api/search)
- 健康检查 (/api/health)
"""

import logging
import os
from typing import Optional

from flask import Flask, jsonify
from flask_cors import CORS

from config import get_config
from database import MongoDBManager
from api import api_bp

# 全局数据库管理器实例
_db_manager: Optional[MongoDBManager] = None


def create_app(config_name: Optional[str] = None) -> Flask:
    """
    创建Flask应用实例
    
    Args:
        config_name: 配置名称，如果为None则使用环境变量FLASK_ENV
        
    Returns:
        Flask: Flask应用实例
    """
    # 获取配置
    config = get_config(config_name)
    
    # 配置日志
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建Flask应用
    app = Flask(__name__)
    app.config.from_object(config)
    
    # 启用CORS
    CORS(app)
    
    # 注册蓝图
    app.register_blueprint(api_bp)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 注册根路由
    @app.route("/")
    def index():
        """根路径，返回API信息"""
        return jsonify({
            "name": "Dify MongoDB Tools",
            "version": "1.0.0",
            "description": "MongoDB数据操作工具集",
            "endpoints": {
                "save": "/api/save",
                "search": "/api/search",
                "health": "/api/health"
            },
            "docs": "/api/docs" if app.debug else None
        })
    
    return app


def register_error_handlers(app: Flask):
    """注册错误处理器"""
    
    @app.errorhandler(400)
    def bad_request(error):
        """处理400错误"""
        return jsonify({"error": "请求参数错误"}), 400
    
    @app.errorhandler(404)
    def not_found(error):
        """处理404错误"""
        return jsonify({"error": "资源不存在"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """处理500错误"""
        logging.error(f"服务器内部错误: {error}")
        return jsonify({"error": "服务器内部错误"}), 500


def get_db_manager() -> MongoDBManager:
    """
    获取数据库管理器实例（单例模式）
    
    Returns:
        MongoDBManager: 数据库管理器实例
    """
    global _db_manager
    if _db_manager is None:
        config = get_config()
        _db_manager = MongoDBManager(config)
    return _db_manager


def init_app():
    """初始化应用"""
    # 获取配置
    config = get_config()
    
    # 创建应用实例
    app = create_app()
    
    # 初始化数据库连接
    try:
        db_manager = get_db_manager()
        # 测试数据库连接
        db_manager.client.admin.command('ping')
        logging.info("数据库连接成功")
    except Exception as e:
        logging.error(f"数据库连接失败: {e}")
        raise
    
    return app


def main():
    """主函数"""
    try:
        # 初始化应用
        app = init_app()
        
        # 获取配置
        config = get_config()
        
        # 启动应用
        logging.info(f"启动应用 - 主机: {config.HOST}, 端口: {config.PORT}")
        app.run(
            host=config.HOST,
            port=config.PORT,
            debug=config.DEBUG
        )
        
    except KeyboardInterrupt:
        logging.info("应用被中断")
    except Exception as e:
        logging.error(f"应用启动失败: {e}")
        raise
    finally:
        # 清理资源
        if _db_manager:
            _db_manager.close()


if __name__ == "__main__":
    main()
