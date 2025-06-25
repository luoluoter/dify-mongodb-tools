"""
工具函数测试
测试各种工具函数的正确性
"""

import unittest
import json
from datetime import datetime

from utils import (
    safe_json_loads, safe_int_convert, validate_uuid,
    sanitize_data, format_timestamp, build_query_filter,
    build_sort_criteria, paginate_results
)


class TestUtils(unittest.TestCase):
    """工具函数测试类"""
    
    def test_safe_json_loads_valid(self):
        """测试有效JSON解析"""
        valid_json = '{"key": "value", "number": 123}'
        result = safe_json_loads(valid_json)
        
        self.assertEqual(result, {"key": "value", "number": 123})
    
    def test_safe_json_loads_invalid(self):
        """测试无效JSON解析"""
        invalid_json = '{"key": "value", "number": 123'
        result = safe_json_loads(invalid_json)
        
        self.assertIsNone(result)
    
    def test_safe_json_loads_with_default(self):
        """测试带默认值的JSON解析"""
        invalid_json = 'invalid'
        default = {"default": "value"}
        result = safe_json_loads(invalid_json, default)
        
        self.assertEqual(result, default)
    
    def test_safe_json_loads_empty(self):
        """测试空字符串JSON解析"""
        result = safe_json_loads("")
        self.assertIsNone(result)
    
    def test_safe_int_convert_valid(self):
        """测试有效整数转换"""
        self.assertEqual(safe_int_convert("123"), 123)
        self.assertEqual(safe_int_convert(456), 456)
        self.assertEqual(safe_int_convert("0"), 0)
    
    def test_safe_int_convert_invalid(self):
        """测试无效整数转换"""
        self.assertEqual(safe_int_convert("abc"), 0)
        self.assertEqual(safe_int_convert(None), 0)
        self.assertEqual(safe_int_convert(""), 0)
    
    def test_safe_int_convert_with_default(self):
        """测试带默认值的整数转换"""
        self.assertEqual(safe_int_convert("abc", 999), 999)
        self.assertEqual(safe_int_convert(None, -1), -1)
    
    def test_validate_uuid_valid(self):
        """测试有效UUID验证"""
        valid_uuids = [
            "123e4567-e89b-12d3-a456-426614174000",
            "550e8400-e29b-41d4-a716-446655440000",
            "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
        ]
        
        for uuid_str in valid_uuids:
            self.assertTrue(validate_uuid(uuid_str))
    
    def test_validate_uuid_invalid(self):
        """测试无效UUID验证"""
        invalid_uuids = [
            "invalid-uuid",
            "123e4567-e89b-12d3-a456",
            "123e4567-e89b-12d3-a456-42661417400g",
            "",
            "not-a-uuid-at-all"
        ]
        
        for uuid_str in invalid_uuids:
            self.assertFalse(validate_uuid(uuid_str))
    
    def test_sanitize_data(self):
        """测试数据清理"""
        input_data = {
            "key1": "value1",
            "key2": "",
            "key3": None,
            "key4": 0,
            "key5": False
        }
        
        expected = {
            "key1": "value1",
            "key4": 0,
            "key5": False
        }
        
        result = sanitize_data(input_data)
        self.assertEqual(result, expected)
    
    def test_sanitize_data_not_dict(self):
        """测试非字典数据清理"""
        self.assertEqual(sanitize_data("not a dict"), {})
        self.assertEqual(sanitize_data(123), {})
        self.assertEqual(sanitize_data(None), {})
    
    def test_format_timestamp(self):
        """测试时间戳格式化"""
        # 测试有效时间戳
        timestamp = 1640995200000  # 2022-01-01 00:00:00
        result = format_timestamp(timestamp)
        
        self.assertIsInstance(result, str)
        self.assertIn("2022-01-01", result)
    
    def test_format_timestamp_invalid(self):
        """测试无效时间戳格式化"""
        result = format_timestamp("invalid")
        self.assertEqual(result, "invalid")
    
    def test_build_query_filter(self):
        """测试查询过滤器构建"""
        params = {
            "uuid": "test-uuid",
            "title": "test-title",
            "title_contains": "search",
            "created_after": "1640995200000",
            "created_before": "1641081600000"
        }
        
        result = build_query_filter(params)
        
        self.assertEqual(result["uuid"], "test-uuid")
        # title_contains会覆盖title字段，使用正则表达式
        self.assertIn("$regex", result["title"])
        self.assertEqual(result["title"]["$regex"], "search")
        self.assertEqual(result["title"]["$options"], "i")
        self.assertIn("created_at", result)
        self.assertEqual(result["created_at"]["$gte"], 1640995200000)
        self.assertEqual(result["created_at"]["$lte"], 1641081600000)
    
    def test_build_sort_criteria_default(self):
        """测试默认排序条件"""
        result = build_sort_criteria("")
        self.assertEqual(result, [("created_at", -1)])
    
    def test_build_sort_criteria_single(self):
        """测试单个排序条件"""
        result = build_sort_criteria("title:asc")
        self.assertEqual(result, [("title", 1)])
    
    def test_build_sort_criteria_multiple(self):
        """测试多个排序条件"""
        result = build_sort_criteria("title:desc,created_at:asc")
        self.assertEqual(result, [("title", -1), ("created_at", 1)])
    
    def test_paginate_results(self):
        """测试结果分页"""
        results = list(range(25))  # 0-24
        
        # 第一页
        page1 = paginate_results(results, page=1, per_page=10)
        self.assertEqual(len(page1["data"]), 10)
        self.assertEqual(page1["data"], list(range(10)))
        self.assertEqual(page1["pagination"]["page"], 1)
        self.assertEqual(page1["pagination"]["total"], 25)
        self.assertEqual(page1["pagination"]["pages"], 3)
        self.assertFalse(page1["pagination"]["has_prev"])
        self.assertTrue(page1["pagination"]["has_next"])
        
        # 第二页
        page2 = paginate_results(results, page=2, per_page=10)
        self.assertEqual(len(page2["data"]), 10)
        self.assertEqual(page2["data"], list(range(10, 20)))
        self.assertTrue(page2["pagination"]["has_prev"])
        self.assertTrue(page2["pagination"]["has_next"])
        
        # 最后一页
        page3 = paginate_results(results, page=3, per_page=10)
        self.assertEqual(len(page3["data"]), 5)
        self.assertEqual(page3["data"], list(range(20, 25)))
        self.assertTrue(page3["pagination"]["has_prev"])
        self.assertFalse(page3["pagination"]["has_next"])


if __name__ == '__main__':
    unittest.main() 