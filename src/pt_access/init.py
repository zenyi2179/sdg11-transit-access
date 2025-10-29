"""
SDG 11 公共交通可达性分析工具包

提供公共交通可达性缓冲区分析、公平性评估和数据处理功能
主要功能：
- 公共交通站点缓冲区分析
- 人口可达性基尼系数计算
- 公交数据网络爬取
- 坐标系统转换
"""

__version__ = "1.0.0"
__author__ = "SDG Research Team"

from .buffer import SDGBufferAnalyzer
from .gini import GiniCalculator
from .crawlers import BusDataCrawler
from .coordinate import CoordinateConverter
from .utils import SpatialUtils, FileProcessor

__all__ = [
    'SDGBufferAnalyzer',
    'GiniCalculator', 
    'BusDataCrawler',
    'CoordinateConverter',
    'SpatialUtils',
    'FileProcessor'
]