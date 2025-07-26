"""
Flask API配置
"""

import os
from datetime import timedelta


class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'spark-ai-secret-key-2024'
    
    # Session配置
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_FILE_DIR = './flask_session'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # CORS配置
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
    CORS_SUPPORTS_CREDENTIALS = True
    
    # API配置
    API_VERSION = 'v1'
    API_PREFIX = '/api'
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False
    
    # 开发环境允许所有来源
    CORS_ORIGINS = ['*']


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    
    # 生产环境严格的CORS设置
    CORS_ORIGINS = [
        'https://your-frontend-domain.com',
        'https://spark-ai.com'
    ]
    
    # 生产环境使用Redis存储session
    SESSION_TYPE = 'redis'
    SESSION_REDIS = os.environ.get('REDIS_URL', 'redis://localhost:6379')


class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    TESTING = True
    
    # 测试环境使用文件系统存储
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = './test_flask_session'


# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}