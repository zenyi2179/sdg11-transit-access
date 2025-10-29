#!/usr/bin/env python3
"""
人口数据处理脚本

功能：
- 处理人口栅格数据
- 提取有效服务区域内人口
- 生成人口可达性分析结果
"""

import sys
import os
import argparse

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from pt_access.buffer import SDGBufferAnalyzer
from pt_access.utils import FileProcessor


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='处理人口数据')
    parser.add_argument('--population-raster', required=True, help='人口栅格数据路径')
    parser.add_argument('--boundary', required=True, help='研究区域边界')
    parser.add_argument('--valid-area', required=True, help='有效服务区域')
    parser.add_argument('--output-dir', default='./output', help='输出目录')
    
    args = parser.parse_args()
    
    # 创建输出目录
    FileProcessor.ensure_directory(args.output_dir)
    
    # 输出文件路径
    pop_all_tif = os.path.join(args.output_dir, 'population_all.tif')
    pop_valid_tif = os.path.join(args.output_dir, 'population_valid.tif')
    pop_points_shp = os.path.join(args.output_dir, 'population_points.shp')
    
    print("开始处理人口数据...")
    
    try:
        # 创建缓冲区分析器
        analyzer = SDGBufferAnalyzer(args.output_dir)
        
        # 按边界提取总人口
        print("提取研究区域总人口...")
        analyzer.extract_by_mask(
            args.population_raster, 
            args.boundary, 
            pop_all_tif
        )
        
        # 按有效区域提取可达人口
        print("提取有效服务区域人口...")
        analyzer.extract_by_mask(
            args.population_raster, 
            args.valid_area, 
            pop_valid_tif
        )
        
        # 将可达人口栅格转为点
        print("转换人口栅格为点数据...")
        analyzer.raster_to_point(pop_valid_tif, pop_points_shp)
        
        print(f"\n人口数据处理完成！")
        print(f"总人口栅格: {pop_all_tif}")
        print(f"可达人口栅格: {pop_valid_tif}")
        print(f"人口点数据: {pop_points_shp}")
        
    except Exception as e:
        print(f"人口数据处理失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()