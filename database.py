"""
数据库操作模块
封装MongoDB的增删改查操作
"""

import json
import time
import uuid
import logging
from typing import Dict, List, Any, Optional, Union
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError

from config import Config

logger = logging.getLogger(__name__)


class MongoDBManager:
    """MongoDB管理器"""
    
    def __init__(self, config: Config):
        """
        初始化MongoDB管理器
        
        Args:
            config: 配置实例
        """
        self.config = config
        self.client = MongoClient(config.MONGO_URI)
        
    def get_database(self, db_name: str) -> Database:
        """
        获取数据库实例
        
        Args:
            db_name: 数据库名称
            
        Returns:
            Database: 数据库实例
        """
        return self.client[db_name]
    
    def get_collection(self, db_name: str, collection_name: str) -> Collection:
        """
        获取集合实例
        
        Args:
            db_name: 数据库名称
            collection_name: 集合名称
            
        Returns:
            Collection: 集合实例
        """
        db = self.get_database(db_name)
        return db[collection_name]
    
    def generate_uuid(self) -> str:
        """
        生成UUID
        
        Returns:
            str: UUID字符串
        """
        return str(uuid.uuid4())
    
    def get_current_timestamp(self) -> int:
        """
        获取当前时间戳（毫秒）
        
        Returns:
            int: 毫秒时间戳
        """
        return int(time.time_ns() // 1000000)
    
    def parse_json_content(self, content: str) -> Dict[str, Any]:
        """
        解析JSON内容
        
        Args:
            content: JSON字符串
            
        Returns:
            Dict[str, Any]: 解析后的字典
        """
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON解析失败: {e}")
            return {}
    
    def save_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        保存数据到指定数据库和集合
        
        Args:
            data: 要保存的数据
            
        Returns:
            Dict[str, Any]: 操作结果
        """
        try:
            # 获取目标数据库和集合
            db_name = data.get("db_name")
            collection_name = data.get("collection_name")
            
            if not db_name or not collection_name:
                return {
                    "error": "必须指定 db_name 和 collection_name",
                    "message": "Missing required parameters"
                }
            
            target_collection = self.get_collection(db_name, collection_name)
            
            # 构建查询条件
            uuid_name = data.get("uuid_name", "uuid")
            uuid_value = data.get("uuid", self.generate_uuid())
            find_obj = {uuid_name: uuid_value}
            
            # 解析content字段
            if "content" in data:
                parsed_data = self.parse_json_content(data.get("content", "{}"))
                if isinstance(parsed_data, list):
                    parsed_data = {"list": parsed_data}
                data["data"] = parsed_data
            else:
                data["data"] = {}
            
            # 添加时间戳
            now_timestamp = self.get_current_timestamp()
            data["data"]["updated_at"] = now_timestamp
            
            # 插入或更新数据
            result = target_collection.update_one(
                find_obj, 
                {"$set": data["data"]}, 
                upsert=True
            )
            
            # 如果是新插入的数据，添加创建时间
            if result.upserted_id:
                data["data"]["created_at"] = now_timestamp
                target_collection.update_one(
                    find_obj, 
                    {"$set": {"created_at": now_timestamp}}
                )
            
            logger.info(f"数据保存成功，数据库: {db_name}, 集合: {collection_name}, ID: {find_obj}")
            return {
                "message": "Data saved successfully",
                "id": find_obj,
                "is_new": bool(result.upserted_id)
            }
            
        except PyMongoError as e:
            logger.error(f"数据库操作失败: {e}")
            raise
    
    def search_data(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        搜索数据
        
        支持复杂的查询条件、排序和分页，可指定目标数据库和集合
        
        Args:
            query_params: 查询参数
            
        Returns:
            List[Dict[str, Any]]: 查询结果列表
        """
        try:
            # 获取目标数据库和集合
            db_name = query_params.get("db_name")
            collection_name = query_params.get("collection_name")
            
            if not db_name or not collection_name:
                return []
            
            target_collection = self.get_collection(db_name, collection_name)
            
            # 构建查询条件
            find_obj = {}
            uuid_name = query_params.get("uuid_name", "uuid")
            uuid_value = query_params.get("uuid")
            
            if uuid_name and uuid_value:
                find_obj[uuid_name] = uuid_value
            
            # 解析额外查询条件
            conditions = query_params.get("conditions")
            if conditions:
                try:
                    parsed_conditions = json.loads(conditions)
                    find_obj.update(parsed_conditions)
                except json.JSONDecodeError as e:
                    logger.error(f"查询条件解析失败: {e}")
            
            # 如果没有查询条件，返回空列表
            if not find_obj and not conditions:
                return []
            
            # 构建排序条件
            sort_obj = {self.config.DEFAULT_SORT_FIELD: self.config.DEFAULT_SORT_ORDER}
            sorts = query_params.get("sorts")
            if sorts:
                try:
                    sort_obj = json.loads(sorts)
                except json.JSONDecodeError as e:
                    logger.error(f"排序条件解析失败: {e}")
            
            # 获取分页参数
            limit = int(query_params.get("limit", self.config.DEFAULT_LIMIT))
            skip = int(query_params.get("skip", self.config.DEFAULT_SKIP))
            
            logger.info(f"查询数据库: {db_name}, 集合: {collection_name}, 条件: {find_obj}, 排序: {sort_obj}")
            
            # 执行查询
            results = list(
                target_collection.find(find_obj, {"_id": 0})
                .skip(skip)
                .limit(limit)
                .sort(sort_obj)
            )
            
            return results
            
        except PyMongoError as e:
            logger.error(f"数据库查询失败: {e}")
            raise
    
    def close(self):
        """关闭数据库连接"""
        if self.client:
            self.client.close() 