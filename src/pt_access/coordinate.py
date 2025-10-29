"""
坐标系转换模块

主要功能：
- GCJ02坐标系转WGS84坐标系
- 批量坐标转换
- 坐标数据导出
"""

import math
import pandas as pd
import os
import csv
from typing import List, Tuple, Optional
import numpy as np


class CoordinateConverter:
    """坐标系转换器"""
    
    # 坐标系参数
    PI = 3.1415926535897932384626  # π
    A = 6378245.0  # 长半轴
    EE = 0.00669342162296594323  # 扁率
    
    def __init__(self):
        """初始化坐标转换器"""
        pass
    
    def transform_lat(self, lng: float, lat: float) -> float:
        """
        纬度转换
        
        Args:
            lng: 经度
            lat: 纬度
            
        Returns:
            转换后的纬度偏移量
        """
        ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
              0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
        ret += (20.0 * math.sin(6.0 * lng * self.PI) + 20.0 *
                math.sin(2.0 * lng * self.PI)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lat * self.PI) + 40.0 *
                math.sin(lat / 3.0 * self.PI)) * 2.0 / 3.0
        ret += (160.0 * math.sin(lat / 12.0 * self.PI) + 320 *
                math.sin(lat * self.PI / 30.0)) * 2.0 / 3.0
        return ret
    
    def transform_lng(self, lng: float, lat: float) -> float:
        """
        经度转换
        
        Args:
            lng: 经度
            lat: 纬度
            
        Returns:
            转换后的经度偏移量
        """
        ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
              0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
        ret += (20.0 * math.sin(6.0 * lng * self.PI) + 20.0 *
                math.sin(2.0 * lng * self.PI)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lng * self.PI) + 40.0 *
                math.sin(lng / 3.0 * self.PI)) * 2.0 / 3.0
        ret += (150.0 * math.sin(lng / 12.0 * self.PI) + 300.0 *
                math.sin(lng / 30.0 * self.PI)) * 2.0 / 3.0
        return ret
    
    def is_out_of_china(self, lng: float, lat: float) -> bool:
        """
        判断坐标是否在中国境外
        
        Args:
            lng: 经度
            lat: 纬度
            
        Returns:
            是否在境外
        """
        if lng < 72.004 or lng > 137.8347:
            return True
        if lat < 0.8293 or lat > 55.8271:
            return True
        return False
    
    def gcj02_to_wgs84(self, lng: float, lat: float) -> Tuple[float, float]:
        """
        GCJ02坐标系转WGS84坐标系
        
        Args:
            lng: GCJ02经度
            lat: GCJ02纬度
            
        Returns:
            (WGS84经度, WGS84纬度)
        """
        # 如果在国外，直接返回原坐标
        if self.is_out_of_china(lng, lat):
            return lng, lat
        
        # 计算偏移量
        dlat = self.transform_lat(lng - 105.0, lat - 35.0)
        dlng = self.transform_lng(lng - 105.0, lat - 35.0)
        
        radlat = lat / 180.0 * self.PI
        magic = math.sin(radlat)
        magic = 1 - self.EE * magic * magic
        sqrtmagic = math.sqrt(magic)
        
        dlat = (dlat * 180.0) / ((self.A * (1 - self.EE)) / (magic * sqrtmagic) * self.PI)
        dlng = (dlng * 180.0) / (self.A / sqrtmagic * math.cos(radlat) * self.PI)
        
        mglat = lat + dlat
        mglng = lng + dlng
        
        # 转换回WGS84
        wgs84_lng = lng * 2 - mglng
        wgs84_lat = lat * 2 - mglat
        
        return wgs84_lng, wgs84_lat
    
    def batch_convert_gcj02_to_wgs84(self, input_file: str, output_file: str = None,
                                   lng_col: str = 'longitude', 
                                   lat_col: str = 'latitude',
                                   name_col: str = 'name') -> pd.DataFrame:
        """
        批量转换GCJ02坐标到WGS84
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            lng_col: 经度列名
            lat_col: 纬度列名  
            name_col: 名称列名
            
        Returns:
            转换后的DataFrame
        """
        # 读取输入文件
        if input_file.endswith('.xlsx'):
            df = pd.read_excel(input_file)
        elif input_file.endswith('.csv'):
            df = pd.read_csv(input_file)
        else:
            raise ValueError("支持的文件格式: .xlsx, .csv")
        
        # 检查必需的列
        required_cols = [lng_col, lat_col, name_col]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"缺少必需的列: {missing_cols}")
        
        # 坐标转换
        wgs84_coords = []
        converted_count = 0
        
        for idx, row in df.iterrows():
            try:
                lng_gcj02 = float(row[lng_col])
                lat_gcj02 = float(row[lat_col])
                
                lng_wgs84, lat_wgs84 = self.gcj02_to_wgs84(lng_gcj02, lat_gcj02)
                wgs84_coords.append((lng_wgs84, lat_wgs84))
                converted_count += 1
                
            except (ValueError, TypeError) as e:
                print(f"第 {idx+1} 行坐标转换失败: {e}")
                wgs84_coords.append((None, None))
        
        # 添加转换后的坐标列
        df['longitude_wgs84'] = [coord[0] for coord in wgs84_coords]
        df['latitude_wgs84'] = [coord[1] for coord in wgs84_coords]
        
        print(f"坐标转换完成！成功转换 {converted_count}/{len(df)} 个坐标")
        
        # 保存结果
        if output_file:
            if output_file.endswith('.xlsx'):
                df.to_excel(output_file, index=False)
            else:
                df.to_csv(output_file, index=False)
            print(f"转换结果已保存到: {output_file}")
        
        return df
    
    def convert_single_point(self, lng: float, lat: float, 
                           source_crs: str = 'GCJ02') -> Tuple[float, float]:
        """
        转换单个坐标点
        
        Args:
            lng: 经度
            lat: 纬度
            source_crs: 源坐标系 ('GCJ02')
            
        Returns:
            (目标经度, 目标纬度)
        """
        if source_crs.upper() == 'GCJ02':
            return self.gcj02_to_wgs84(lng, lat)
        else:
            raise ValueError(f"不支持的坐标系: {source_crs}")
    
    def validate_coordinates(self, coordinates: List[Tuple[float, float]]) -> List[bool]:
        """
        验证坐标是否有效
        
        Args:
            coordinates: 坐标列表 [(lng, lat), ...]
            
        Returns:
            有效性列表 [True/False, ...]
        """
        validations = []
        
        for lng, lat in coordinates:
            is_valid = (
                -180 <= lng <= 180 and 
                -90 <= lat <= 90 and
                not math.isnan(lng) and 
                not math.isnan(lat)
            )
            validations.append(is_valid)
        
        return validations