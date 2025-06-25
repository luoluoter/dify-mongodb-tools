"""
配置管理模块
集中管理应用程序的所有配置项
"""

import os
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """应用程序配置类"""
    
    # MongoDB 配置
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    
    # Flask 应用配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "3333"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # API 配置
    DEFAULT_LIMIT: int = 5
    DEFAULT_SKIP: int = 0
    DEFAULT_SORT_FIELD: str = "created_at"
    DEFAULT_SORT_ORDER: int = -1  # -1 for descending, 1 for ascending


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = "WARNING"


class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


# 配置映射
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}


def get_config(config_name: Optional[str] = None) -> Config:
    """
    获取配置实例
    
    Args:
        config_name: 配置名称，如果为None则使用环境变量FLASK_ENV
        
    Returns:
        Config: 配置实例
    """
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "default")
    
    config_class = config_map.get(config_name, config_map["default"])
    return config_class() 