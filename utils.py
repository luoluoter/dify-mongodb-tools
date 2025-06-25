"""
工具函数模块
提供通用的工具函数和辅助方法
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


def safe_json_loads(data: str, default: Any = None) -> Any:
    """
    安全的JSON解析函数
    
    Args:
        data: 要解析的JSON字符串
        default: 解析失败时的默认值
        
    Returns:
        解析后的数据或默认值
    """
    try:
        return json.loads(data) if data else default
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"JSON解析失败: {e}, 数据: {data}")
        return default


def safe_int_convert(value: Any, default: int = 0) -> int:
    """
    安全的整数转换函数
    
    Args:
        value: 要转换的值
        default: 转换失败时的默认值
        
    Returns:
        转换后的整数或默认值
    """
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def validate_uuid(uuid_str: str) -> bool:
    """
    验证UUID格式
    
    Args:
        uuid_str: 要验证的UUID字符串
        
    Returns:
        bool: 是否为有效的UUID格式
    """
    import re
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(uuid_str))


def sanitize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    清理和验证数据
    
    Args:
        data: 要清理的数据字典
        
    Returns:
        Dict[str, Any]: 清理后的数据
    """
    if not isinstance(data, dict):
        return {}
    
    # 移除None值和空字符串
    cleaned_data = {}
    for key, value in data.items():
        if value is not None and value != "":
            cleaned_data[key] = value
    
    return cleaned_data


def format_timestamp(timestamp: int) -> str:
    """
    格式化时间戳为可读字符串
    
    Args:
        timestamp: 毫秒时间戳
        
    Returns:
        str: 格式化的时间字符串
    """
    try:
        dt = datetime.fromtimestamp(timestamp / 1000)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return str(timestamp)


def build_query_filter(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    构建MongoDB查询过滤器
    
    Args:
        params: 查询参数字典
        
    Returns:
        Dict[str, Any]: MongoDB查询过滤器
    """
    query_filter = {}
    
    # 处理精确匹配
    for field in ['uuid', 'title', 'type']:
        if params.get(field):
            query_filter[field] = params[field]
    
    # 处理模糊匹配
    if params.get('title_contains'):
        query_filter['title'] = {
            '$regex': params['title_contains'],
            '$options': 'i'
        }
    
    # 处理时间范围
    if params.get('created_after'):
        query_filter.setdefault('created_at', {})
        query_filter['created_at']['$gte'] = int(params['created_after'])
    
    if params.get('created_before'):
        query_filter.setdefault('created_at', {})
        query_filter['created_at']['$lte'] = int(params['created_before'])
    
    return query_filter


def build_sort_criteria(sort_param: str, default_field: str = "created_at") -> List[tuple]:
    """
    构建排序条件
    
    Args:
        sort_param: 排序参数字符串，格式: "field:order,field2:order2"
        default_field: 默认排序字段
        
    Returns:
        List[tuple]: 排序条件列表
    """
    if not sort_param:
        return [(default_field, -1)]
    
    sort_criteria = []
    for sort_item in sort_param.split(','):
        if ':' in sort_item:
            field, order = sort_item.split(':', 1)
            order_int = -1 if order.lower() in ['desc', '-1', 'descending'] else 1
            sort_criteria.append((field.strip(), order_int))
        else:
            sort_criteria.append((sort_item.strip(), -1))
    
    return sort_criteria if sort_criteria else [(default_field, -1)]


def paginate_results(results: List[Any], page: int = 1, per_page: int = 10) -> Dict[str, Any]:
    """
    分页处理结果
    
    Args:
        results: 结果列表
        page: 页码（从1开始）
        per_page: 每页数量
        
    Returns:
        Dict[str, Any]: 分页后的结果
    """
    total = len(results)
    start = (page - 1) * per_page
    end = start + per_page
    
    return {
        'data': results[start:end],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'has_prev': page > 1,
            'has_next': end < total
        }
    }


def log_request_info(request_data: Dict[str, Any], endpoint: str):
    """
    记录请求信息
    
    Args:
        request_data: 请求数据
        endpoint: 端点名称
    """
    logger.info(f"API请求 - 端点: {endpoint}, 数据: {request_data}")


def log_response_info(response_data: Any, endpoint: str, status_code: int = 200):
    """
    记录响应信息
    
    Args:
        response_data: 响应数据
        endpoint: 端点名称
        status_code: 状态码
    """
    if status_code >= 400:
        logger.error(f"API响应 - 端点: {endpoint}, 状态码: {status_code}, 错误: {response_data}")
    else:
        logger.info(f"API响应 - 端点: {endpoint}, 状态码: {status_code}") 