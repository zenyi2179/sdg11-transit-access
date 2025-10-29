"""
公交数据网络爬虫模块

主要功能：
- 从8684网站爬取公交线路信息
- 从高德地图API获取站点坐标
- 数据清洗和整理
"""

import requests
from bs4 import BeautifulSoup
import json
import xlwt
import re
from typing import List, Dict, Set, Optional
import time
import urllib.request
import urllib.error


class BusDataCrawler:
    """公交数据爬取器"""
    
    def __init__(self, user_agent: str = None):
        """
        初始化爬虫
        
        Args:
            user_agent: 用户代理字符串
        """
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
    
    def get_bus_categories(self, city: str) -> Dict[str, str]:
        """
        获取公交线路分类信息
        
        Args:
            city: 城市拼音（如wuhan）
            
        Returns:
            分类字典 {分类名称: 链接}
        """
        url = f'https://{city}.8684.cn/'
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            soup_buslayer = soup.find('div', class_='bus-layer depth w120')
            
            if not soup_buslayer:
                raise Exception("未找到公交分类信息")
            
            categories = {}
            soup_buslist = soup_buslayer.find_all('div', class_='pl10')
            
            for soup_bus in soup_buslist:
                name = soup_bus.find('span', class_='kt').get_text()
                if '线路分类' in name:
                    soup_a_list = soup_bus.find('div', class_='list')
                    for soup_a in soup_a_list.find_all('a'):
                        text = soup_a.get_text()
                        href = soup_a.get('href')
                        categories[text] = f"https://{city}.8684.cn{href}"
            
            return categories
            
        except Exception as e:
            raise Exception(f"获取公交分类失败: {e}")
    
    def get_bus_lines(self, category_url: str) -> List[Dict[str, str]]:
        """
        获取指定分类下的公交线路
        
        Args:
            category_url: 分类页面URL
            
        Returns:
            公交线路列表
        """
        try:
            response = self.session.get(category_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            bus_lines = []
            
            soup_buslist = soup.find('div', class_='list clearfix')
            if soup_buslist:
                for soup_a in soup_buslist.find_all('a'):
                    title = soup_a.get('title', '')
                    text = soup_a.get_text()
                    href = soup_a.get('href')
                    
                    if href:
                        full_url = f"https://{category_url.split('/')[2]}{href}"
                        bus_lines.append({
                            'title': title,
                            'name': text,
                            'url': full_url
                        })
            
            return bus_lines
            
        except Exception as e:
            raise Exception(f"获取公交线路失败: {e}")
    
    def get_bus_stops_from_line(self, line_url: str) -> Set[str]:
        """
        从线路页面获取公交站点
        
        Args:
            line_url: 线路页面URL
            
        Returns:
            站点名称集合
        """
        try:
            response = self.session.get(line_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            stops = set()
            
            soup_buslayer = soup.find('div', class_='bus-lzlist mb15')
            if soup_buslayer:
                for ol in soup_buslayer.find_all('ol'):
                    for li in ol.find_all('li'):
                        bus_stop = li.find('a')
                        if bus_stop:
                            text = bus_stop.get('aria-label')
                            if text:
                                stop_name = text.split()[1]  # 提取站点名称
                                stops.add(stop_name)
            
            return stops
            
        except Exception as e:
            print(f"获取线路站点失败 {line_url}: {e}")
            return set()
    
    def crawl_all_bus_stops(self, city: str, output_file: str = None) -> Set[str]:
        """
        爬取城市所有公交站点
        
        Args:
            city: 城市拼音
            output_file: 输出文件路径
            
        Returns:
            站点名称集合
        """
        print(f"开始爬取 {city} 的公交站点数据...")
        
        # 获取分类信息
        categories = self.get_bus_categories(city)
        print(f"找到 {len(categories)} 个分类")
        
        all_stops = set()
        line_count = 0
        
        # 遍历每个分类
        for category_name, category_url in categories.items():
            print(f"处理分类: {category_name}")
            
            # 获取该分类下的所有线路
            bus_lines = self.get_bus_lines(category_url)
            print(f"  找到 {len(bus_lines)} 条线路")
            
            # 遍历每条线路获取站点
            for i, line in enumerate(bus_lines):
                stops = self.get_bus_stops_from_line(line['url'])
                all_stops.update(stops)
                line_count += 1
                
                if i % 10 == 0:
                    print(f"  已处理 {i+1}/{len(bus_lines)} 条线路，累计站点: {len(all_stops)}")
                
                # 避免请求过于频繁
                time.sleep(0.1)
        
        print(f"爬取完成！共处理 {line_count} 条线路，获取 {len(all_stops)} 个唯一站点")
        
        # 保存到文件
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                for stop in sorted(all_stops):
                    f.write(stop + '\n')
            print(f"站点数据已保存到: {output_file}")
        
        return all_stops
    
    def get_coordinates_from_gaode(self, bus_stop: str, city: str, 
                                 api_key: str) -> Optional[Dict[str, float]]:
        """
        从高德地图API获取站点坐标
        
        Args:
            bus_stop: 公交站点名称
            city: 城市名称（中文）
            api_key: 高德API密钥
            
        Returns:
            坐标字典 {'lng': 经度, 'lat': 纬度}
        """
        url = 'https://restapi.amap.com/v3/geocode/geo'
        address = f"{bus_stop}公交站"
        
        params = {
            'key': api_key,
            'address': address,
            'city': city
        }
        
        try:
            response = self.session.get(url, params=params)
            data = response.json()
            
            if data.get('status') == '1' and data.get('geocodes'):
                location = data['geocodes'][0]['location']
                lng, lat = map(float, location.split(','))
                return {'lng': lng, 'lat': lat}
            else:
                print(f"未找到站点坐标: {bus_stop}")
                return None
                
        except Exception as e:
            print(f"获取坐标失败 {bus_stop}: {e}")
            return None
    
    def export_stops_to_excel(self, stops: Set[str], city: str, 
                            api_key: str, output_file: str):
        """
        导出站点数据到Excel（包含坐标）
        
        Args:
            stops: 站点集合
            city: 城市名称（中文）
            api_key: 高德API密钥
            output_file: 输出文件路径
        """
        wb = xlwt.Workbook()
        ws = wb.add_sheet('公交站点')
        
        # 写入表头
        headers = ['序号', '站点名称', '经度', '纬度']
        for i, header in enumerate(headers):
            ws.write(0, i, header)
        
        # 写入站点数据
        successful_count = 0
        for i, stop in enumerate(sorted(stops), 1):
            ws.write(i, 0, i)  # 序号
            ws.write(i, 1, stop)  # 站点名称
            
            # 获取坐标
            coords = self.get_coordinates_from_gaode(stop, city, api_key)
            if coords:
                ws.write(i, 2, coords['lng'])
                ws.write(i, 3, coords['lat'])
                successful_count += 1
            else:
                ws.write(i, 2, '未获取')
                ws.write(i, 3, '未获取')
            
            # 显示进度
            if i % 10 == 0:
                print(f"已处理 {i}/{len(stops)} 个站点，成功获取 {successful_count} 个坐标")
            
            # 避免API请求过于频繁
            time.sleep(0.2)
        
        wb.save(output_file)
        print(f"数据导出完成！成功获取 {successful_count}/{len(stops)} 个站点的坐标")