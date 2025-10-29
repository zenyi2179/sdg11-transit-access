"""
项目配置文件

功能：
- 定义项目全局配置参数
- 设置默认文件路径和参数
- 管理环境变量和API密钥
"""

import os
from typing import Dict, Any


class Config:
    """项目配置类"""
    
    # 基础路径配置
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
    
    # 数据子目录
    RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
    INTERIM_DATA_DIR = os.path.join(DATA_DIR, 'interim') 
    FINAL_DATA_DIR = os.path.join(DATA_DIR, 'final')
    
    # 公共交通数据配置
    TRAFFIC_DATA_PATHS = {
        'bus_stops': os.path.join(RAW_DATA_DIR, 'bus_stop_poi.shp'),
        'tram_stops': os.path.join(RAW_DATA_DIR, 'tram_stop_poi.shp'),
        'railway_stations': os.path.join(RAW_DATA_DIR, 'railway_station_poi.shp'),
        'ferry_terminals': os.path.join(RAW_DATA_DIR, 'ferry_terminal_poi.shp')
    }
    
    # 人口数据配置
    POPULATION_DATA_PATHS = {
        'population_raster': os.path.join(RAW_DATA_DIR, 'rus_ppp_2020_constrained.tif'),
        'boundary': os.path.join(RAW_DATA_DIR, 'boundary.shp')
    }
    
    # 缓冲区分析参数
    BUFFER_DISTANCES = {
        'bus_stop': 500,      # 公交站点缓冲区距离（米）
        'other_transit': 1000 # 其他交通站点缓冲区距离（米）
    }
    
    # 空间分析参数
    SPATIAL_ANALYSIS = {
        'coordinate_system': 'WGS84',
        'distance_unit': 'Meters',
        'default_tolerance': 1.0
    }
    
    # API配置
    API_KEYS = {
        'gaode_map': os.getenv('GAODE_MAP_API_KEY', 'your_gaode_api_key_here')
    }
    
    # 网络爬虫配置
    CRAWLER_CONFIG = {
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'request_delay': 0.1,  # 请求延迟（秒）
        'max_retries': 3       # 最大重试次数
    }
    
    # 基尼系数计算参数
    GINI_CONFIG = {
        'output_precision': 4,  # 输出精度（小数位数）
        'export_format': 'xlsx' # 导出格式
    }
    
    @classmethod
    def create_directories(cls):
        """创建必要的目录结构"""
        directories = [
            cls.DATA_DIR,
            cls.RAW_DATA_DIR,
            cls.INTERIM_DATA_DIR,
            cls.FINAL_DATA_DIR,
            cls.OUTPUT_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def get_city_config(cls, city_name: str) -> Dict[str, Any]:
        """
        获取城市特定配置
        
        Args:
            city_name: 城市名称
            
        Returns:
            城市配置字典
        """
        city_configs = {
            'wuhan': {
                'name_chinese': '武汉',
                'name_pinyin': 'wuhan',
                'boundary_file': os.path.join(cls.RAW_DATA_DIR, 'wuhan_boundary.shp'),
                'population_file': os.path.join(cls.RAW_DATA_DIR, 'wuhan_population.tif')
            },
            'shanghai': {
                'name_chinese': '上海', 
                'name_pinyin': 'shanghai',
                'boundary_file': os.path.join(cls.RAW_DATA_DIR, 'shanghai_boundary.shp'),
                'population_file': os.path.join(cls.RAW_DATA_DIR, 'shanghai_population.tif')
            },
            'beijing': {
                'name_chinese': '北京',
                'name_pinyin': 'beijing', 
                'boundary_file': os.path.join(cls.RAW_DATA_DIR, 'beijing_boundary.shp'),
                'population_file': os.path.join(cls.RAW_DATA_DIR, 'beijing_population.tif')
            }
        }
        
        return city_configs.get(city_name.lower(), {})
    
    @classmethod
    def validate_config(cls) -> bool:
        """
        验证配置完整性
        
        Returns:
            配置是否有效
        """
        # 检查必要目录
        required_dirs = [cls.DATA_DIR, cls.OUTPUT_DIR]
        for directory in required_dirs:
            if not os.path.exists(directory):
                print(f"警告: 目录不存在: {directory}")
        
        # 检查API密钥
        if cls.API_KEYS['gaode_map'] == 'your_gaode_api_key_here':
            print("警告: 高德地图API密钥未配置")
        
        return True


# 创建默认目录结构
Config.create_directories()