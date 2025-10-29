#!/usr/bin/env python3
"""
公交数据下载脚本

功能：
- 从8684网站下载公交线路和站点数据
- 从高德地图API获取站点坐标
- 导出为Excel格式
"""

import sys
import os
import argparse
from typing import Dict, List

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from pt_access.crawlers import BusDataCrawler


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='下载公交站点数据')
    parser.add_argument('city_pinyin', help='城市拼音（如：wuhan）')
    parser.add_argument('city_chinese', help='城市中文名（如：武汉）')
    parser.add_argument('--api-key', required=True, help='高德地图API密钥')
    parser.add_argument('--output-dir', default='./output', help='输出目录')
    parser.add_argument('--max-lines', type=int, default=1000, help='最大处理线路数')
    
    args = parser.parse_args()
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 输出文件路径
    stops_file = os.path.join(args.output_dir, f'{args.city_pinyin}_bus_stops.txt')
    excel_file = os.path.join(args.output_dir, f'{args.city_pinyin}_bus_stops.xls')
    
    print(f"开始下载 {args.city_chinese} 的公交数据...")
    print(f"城市拼音: {args.city_pinyin}")
    print(f"输出目录: {args.output_dir}")
    
    try:
        # 创建爬虫实例
        crawler = BusDataCrawler()
        
        # 爬取公交站点
        print("正在爬取公交站点数据...")
        bus_stops = crawler.crawl_all_bus_stops(
            city=args.city_pinyin,
            output_file=stops_file
        )
        
        # 导出带坐标的Excel文件
        print("正在获取站点坐标...")
        crawler.export_stops_to_excel(
            stops=bus_stops,
            city=args.city_chinese,
            api_key=args.api_key,
            output_file=excel_file
        )
        
        print(f"\n数据下载完成！")
        print(f"站点列表: {stops_file}")
        print(f"带坐标数据: {excel_file}")
        
    except Exception as e:
        print(f"数据下载失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()