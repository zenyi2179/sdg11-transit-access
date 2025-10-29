#!/usr/bin/env python3
"""
坐标转换脚本

功能：
- 批量转换GCJ02坐标到WGS84
- 支持Excel和CSV格式输入输出
"""

import sys
import os
import argparse
import pandas as pd

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from pt_access.coordinate import CoordinateConverter
from pt_access.utils import FileProcessor


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='批量坐标转换')
    parser.add_argument('input_file', help='输入文件路径（.xlsx或.csv）')
    parser.add_argument('--lng-col', default='longitude', help='经度列名')
    parser.add_argument('--lat-col', default='latitude', help='纬度列名')
    parser.add_argument('--name-col', default='name', help='名称列名')
    parser.add_argument('--output-file', help='输出文件路径')
    parser.add_argument('--source-crs', default='GCJ02', choices=['GCJ02'], 
                       help='源坐标系')
    
    args = parser.parse_args()
    
    # 验证输入文件
    if not FileProcessor.validate_file_path(args.input_file):
        print(f"错误：输入文件不存在: {args.input_file}")
        sys.exit(1)
    
    # 设置输出文件
    if not args.output_file:
        base_name = os.path.splitext(args.input_file)[0]
        if args.input_file.endswith('.xlsx'):
            args.output_file = f"{base_name}_wgs84.xlsx"
        else:
            args.output_file = f"{base_name}_wgs84.csv"
    
    # 确保输出目录存在
    FileProcessor.ensure_directory(os.path.dirname(args.output_file))
    
    print(f"开始坐标转换...")
    print(f"输入文件: {args.input_file}")
    print(f"输出文件: {args.output_file}")
    print(f"源坐标系: {args.source_crs}")
    print(f"经度列: {args.lng_col}, 纬度列: {args.lat_col}, 名称列: {args.name_col}")
    
    try:
        # 创建坐标转换器
        converter = CoordinateConverter()
        
        # 执行批量转换
        result_df = converter.batch_convert_gcj02_to_wgs84(
            input_file=args.input_file,
            output_file=args.output_file,
            lng_col=args.lng_col,
            lat_col=args.lat_col,
            name_col=args.name_col
        )
        
        print(f"\n坐标转换完成！")
        print(f"成功转换 {len(result_df)} 个坐标点")
        print(f"结果文件: {args.output_file}")
        
        # 显示前几行结果
        print(f"\n前5行转换结果:")
        print(result_df.head())
        
    except Exception as e:
        print(f"坐标转换失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()