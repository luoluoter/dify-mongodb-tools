"""
数据库模块测试
测试MongoDB管理器的各项功能
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json

from config import TestingConfig
from database import MongoDBManager


class TestMongoDBManager(unittest.TestCase):
    """MongoDB管理器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.config = TestingConfig()
        with patch('database.MongoClient'):
            self.db_manager = MongoDBManager(self.config)
    
    def test_generate_uuid(self):
        """测试UUID生成"""
        uuid1 = self.db_manager.generate_uuid()
        uuid2 = self.db_manager.generate_uuid()
        
        self.assertIsInstance(uuid1, str)
        self.assertIsInstance(uuid2, str)
        self.assertNotEqual(uuid1, uuid2)
        self.assertTrue(len(uuid1) > 0)
    
    def test_get_current_timestamp(self):
        """测试时间戳生成"""
        timestamp = self.db_manager.get_current_timestamp()
        
        self.assertIsInstance(timestamp, int)
        self.assertTrue(timestamp > 0)
    
    def test_parse_json_content_valid(self):
        """测试有效JSON解析"""
        valid_json = '{"key": "value", "number": 123}'
        result = self.db_manager.parse_json_content(valid_json)
        
        self.assertEqual(result, {"key": "value", "number": 123})
    
    def test_parse_json_content_invalid(self):
        """测试无效JSON解析"""
        invalid_json = '{"key": "value", "number": 123'
        result = self.db_manager.parse_json_content(invalid_json)
        
        self.assertEqual(result, {})
    
    def test_parse_json_content_empty(self):
        """测试空JSON解析"""
        result = self.db_manager.parse_json_content("")
        self.assertEqual(result, {})
    
    def test_save_data_missing_db_name(self):
        """测试缺少数据库名称"""
        data = {
            "collection_name": "test_collection",
            "content": '{"test": "data"}'
        }
        
        result = self.db_manager.save_data(data)
        
        self.assertIn("error", result)
        self.assertEqual(result["message"], "Missing required parameters")
    
    def test_save_data_missing_collection_name(self):
        """测试缺少集合名称"""
        data = {
            "db_name": "test_db",
            "content": '{"test": "data"}'
        }
        
        result = self.db_manager.save_data(data)
        
        self.assertIn("error", result)
        self.assertEqual(result["message"], "Missing required parameters")
    
    def test_save_data_with_custom_db(self):
        """测试保存数据到自定义数据库"""
        data = {
            "db_name": "test_db",
            "collection_name": "test_collection",
            "content": '{"test": "data"}'
        }
        
        # 模拟数据库操作
        mock_result = Mock()
        mock_result.upserted_id = "new_id"
        mock_collection = Mock()
        mock_collection.update_one.return_value = mock_result
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        self.db_manager.client.__getitem__.return_value = mock_db
        
        result = self.db_manager.save_data(data)
        
        self.assertEqual(result["message"], "Data saved successfully")
        self.assertIn("id", result)
    
    def test_save_data_with_list_content(self):
        """测试保存列表内容"""
        data = {
            "db_name": "test_db",
            "collection_name": "test_collection",
            "content": '[{"item": 1}, {"item": 2}]'
        }
        
        # 模拟数据库操作
        mock_result = Mock()
        mock_result.upserted_id = "new_id"
        mock_collection = Mock()
        mock_collection.update_one.return_value = mock_result
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        self.db_manager.client.__getitem__.return_value = mock_db
        
        result = self.db_manager.save_data(data)
        
        self.assertEqual(result["message"], "Data saved successfully")
        # 验证update_one被调用了两次（第一次保存数据，第二次添加created_at）
        self.assertEqual(mock_collection.update_one.call_count, 2)
        
        # 检查第一次调用（保存数据）
        first_call = mock_collection.update_one.call_args_list[0]
        set_data = first_call[0][1]["$set"]
        self.assertIn("list", set_data)
        self.assertEqual(set_data["list"], [{"item": 1}, {"item": 2}])
        self.assertIn("updated_at", set_data)
        
        # 检查第二次调用（添加created_at）
        second_call = mock_collection.update_one.call_args_list[1]
        self.assertIn("created_at", second_call[0][1]["$set"])
    
    def test_search_data_missing_db_name(self):
        """测试搜索缺少数据库名称"""
        query_params = {
            "collection_name": "test_collection"
        }
        
        results = self.db_manager.search_data(query_params)
        
        self.assertEqual(results, [])
    
    def test_search_data_missing_collection_name(self):
        """测试搜索缺少集合名称"""
        query_params = {
            "db_name": "test_db"
        }
        
        results = self.db_manager.search_data(query_params)
        
        self.assertEqual(results, [])
    
    def test_search_data_with_conditions(self):
        """测试带条件的搜索"""
        query_params = {
            "db_name": "test_db",
            "collection_name": "test_collection",
            "conditions": '{"title": "test"}',
            "limit": "10"
        }
        
        # 模拟数据库操作
        mock_collection = Mock()
        mock_collection.find.return_value.skip.return_value.limit.return_value.sort.return_value = []
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        self.db_manager.client.__getitem__.return_value = mock_db
        
        results = self.db_manager.search_data(query_params)
        
        self.assertEqual(results, [])
    
    def test_search_data_with_uuid(self):
        """测试UUID搜索"""
        query_params = {
            "db_name": "test_db",
            "collection_name": "test_collection",
            "uuid": "test-uuid-123",
            "uuid_name": "custom_id"
        }
        
        # 模拟数据库操作
        mock_collection = Mock()
        mock_collection.find.return_value.skip.return_value.limit.return_value.sort.return_value = []
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        self.db_manager.client.__getitem__.return_value = mock_db
        
        results = self.db_manager.search_data(query_params)
        
        self.assertEqual(results, [])
    
    def test_search_data_empty_conditions(self):
        """测试空条件搜索"""
        query_params = {
            "db_name": "test_db",
            "collection_name": "test_collection"
        }
        
        results = self.db_manager.search_data(query_params)
        
        self.assertEqual(results, [])


if __name__ == '__main__':
    unittest.main() 