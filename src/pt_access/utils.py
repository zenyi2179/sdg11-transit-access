"""
通用工具函数模块

主要功能：
- 空间分析工具函数
- 文件处理工具
- 数据验证和清理
"""

import os
import arcpy
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union
import csv
import openpyxl


class SpatialUtils:
    """空间分析工具类"""
    
    @staticmethod
    def check_spatial_reference(feature_class: str) -> Dict[str, Any]:
        """
        检查空间参考信息
        
        Args:
            feature_class: 要素类路径
            
        Returns:
            空间参考信息字典
        """
        try:
            desc = arcpy.Describe(feature_class)
            spatial_ref = desc.spatialReference
            
            return {
                'name': spatial_ref.name,
                'type': spatial_ref.type,
                'factoryCode': spatial_ref.factoryCode,
                'linearUnit': getattr(spatial_ref, 'linearUnitName', 'Unknown'),
                'angularUnit': getattr(spatial_ref, 'angularUnitName', 'Unknown')
            }
        except Exception as e:
            raise Exception(f"检查空间参考失败: {e}")
    
    @staticmethod
    def calculate_feature_statistics(feature_class: str, field: str = None) -> Dict[str, Any]:
        """
        计算要素统计信息
        
        Args:
            feature_class: 要素类路径
            field: 统计字段（可选）
            
        Returns:
            统计信息字典
        """
        try:
            result = {}
            
            # 获取要素数量
            count = arcpy.GetCount_management(feature_class)
            result['feature_count'] = int(count[0])
            
            # 如果指定了字段，计算字段统计
            if field and arcpy.ListFields(feature_class, field):
                field_type = [f.type for f in arcpy.ListFields(feature_class, field)][0]
                
                if field_type in ['Double', 'Single', 'Integer', 'SmallInteger']:
                    # 数值字段统计
                    stats = arcpy.Statistics_analysis(
                        feature_class, 
                        "in_memory/stats", 
                        [[field, "MIN"], [field, "MAX"], [field, "MEAN"], [field, "SUM"]]
                    )
                    
                    with arcpy.da.SearchCursor(stats, ["MIN", "MAX", "MEAN", "SUM"]) as cursor:
                        for row in cursor:
                            result['min'] = row[0]
                            result['max'] = row[1]
                            result['mean'] = row[2]
                            result['sum'] = row[3]
                            break
                    
                    arcpy.Delete_management(stats)
            
            return result
            
        except Exception as e:
            raise Exception(f"计算要素统计失败: {e}")
    
    @staticmethod
    def export_features_to_csv(feature_class: str, output_csv: str, 
                             fields: List[str] = None) -> str:
        """
        导出要素属性到CSV
        
        Args:
            feature_class: 要素类路径
            output_csv: 输出CSV路径
            fields: 要导出的字段列表
            
        Returns:
            输出文件路径
        """
        try:
            if not fields:
                # 获取所有字段（排除几何字段）
                field_names = [f.name for f in arcpy.ListFields(feature_class) 
                             if f.type not in ['Geometry', 'OID']]
            else:
                field_names = fields
            
            # 使用搜索游标读取数据
            data = []
            with arcpy.da.SearchCursor(feature_class, field_names) as cursor:
                for row in cursor:
                    data.append(row)
            
            # 写入CSV
            with open(output_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(field_names)
                writer.writerows(data)
            
            return output_csv
            
        except Exception as e:
            raise Exception(f"导出要素到CSV失败: {e}")
    
    @staticmethod
    def create_spatial_index(feature_class: str) -> bool:
        """
        创建空间索引
        
        Args:
            feature_class: 要素类路径
            
        Returns:
            是否成功创建
        """
        try:
            arcpy.AddSpatialIndex_management(feature_class)
            return True
        except Exception as e:
            print(f"创建空间索引失败: {e}")
            return False


class FileProcessor:
    """文件处理工具类"""
    
    @staticmethod
    def ensure_directory(directory: str) -> bool:
        """
        确保目录存在
        
        Args:
            directory: 目录路径
            
        Returns:
            是否成功
        """
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
            return True
        except Exception as e:
            print(f"创建目录失败 {directory}: {e}")
            return False
    
    @staticmethod
    def read_csv_data(file_path: str, encoding: str = 'utf-8') -> List[List]:
        """
        读取CSV数据
        
        Args:
            file_path: 文件路径
            encoding: 文件编码
            
        Returns:
            数据列表
        """
        data = []
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                csv_reader = csv.reader(f)
                header = next(csv_reader)  # 读取标题行
                for row in csv_reader:
                    data.append(row)
            return data
        except Exception as e:
            raise Exception(f"读取CSV文件失败 {file_path}: {e}")
    
    @staticmethod
    def write_csv_data(data: List[List], file_path: str, 
                      headers: List[str] = None) -> bool:
        """
        写入CSV数据
        
        Args:
            data: 数据列表
            file_path: 文件路径
            headers: 标题行
            
        Returns:
            是否成功
        """
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if headers:
                    writer.writerow(headers)
                writer.writerows(data)
            return True
        except Exception as e:
            print(f"写入CSV文件失败 {file_path}: {e}")
            return False
    
    @staticmethod
    def get_file_list(directory: str, extension: str = None) -> List[str]:
        """
        获取目录下的文件列表
        
        Args:
            directory: 目录路径
            extension: 文件扩展名（可选）
            
        Returns:
            文件路径列表
        """
        if not os.path.exists(directory):
            return []
        
        files = []
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                if extension:
                    if file.lower().endswith(extension.lower()):
                        files.append(file_path)
                else:
                    files.append(file_path)
        
        return files
    
    @staticmethod
    def validate_file_path(file_path: str, check_exists: bool = True) -> bool:
        """
        验证文件路径
        
        Args:
            file_path: 文件路径
            check_exists: 是否检查文件存在
            
        Returns:
            路径是否有效
        """
        try:
            # 检查路径格式
            if not file_path or not isinstance(file_path, str):
                return False
            
            # 检查目录是否存在
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                return False
            
            # 检查文件是否存在
            if check_exists and not os.path.exists(file_path):
                return False
            
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def backup_file(file_path: str, backup_suffix: str = "_backup") -> str:
        """
        备份文件
        
        Args:
            file_path: 原文件路径
            backup_suffix: 备份后缀
            
        Returns:
            备份文件路径
        """
        if not os.path.exists(file_path):
            return ""
        
        try:
            base, ext = os.path.splitext(file_path)
            backup_path = f"{base}{backup_suffix}{ext}"
            
            import shutil
            shutil.copy2(file_path, backup_path)
            return backup_path
            
        except Exception as e:
            print(f"文件备份失败 {file_path}: {e}")
            return ""


class DataValidator:
    """数据验证类"""
    
    @staticmethod
    def validate_coordinate(lng: float, lat: float) -> bool:
        """
        验证坐标有效性
        
        Args:
            lng: 经度
            lat: 纬度
            
        Returns:
            坐标是否有效
        """
        return (-180 <= lng <= 180) and (-90 <= lat <= 90)
    
    @staticmethod
    def validate_population_data(population: float) -> bool:
        """
        验证人口数据
        
        Args:
            population: 人口数量
            
        Returns:
            数据是否有效
        """
        return population >= 0 and not np.isnan(population)
    
    @staticmethod
    def clean_dataframe(df: pd.DataFrame, 
                       drop_na_columns: List[str] = None) -> pd.DataFrame:
        """
        清理DataFrame数据
        
        Args:
            df: 输入DataFrame
            drop_na_columns: 需要删除空值的列
            
        Returns:
            清理后的DataFrame
        """
        cleaned_df = df.copy()
        
        # 删除完全为空的行
        cleaned_df = cleaned_df.dropna(how='all')
        
        # 删除指定列为空的行
        if drop_na_columns:
            cleaned_df = cleaned_df.dropna(subset=drop_na_columns)
        
        # 重置索引
        cleaned_df = cleaned_df.reset_index(drop=True)
        
        return cleaned_df