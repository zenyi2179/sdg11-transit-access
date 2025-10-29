"""
公共交通可达性缓冲区分析模块

主要功能：
- 创建公交站点缓冲区（500m/1000m）
- 计算有效服务区域
- 人口可达性分析
"""

import arcpy
from typing import List, Optional, Tuple
import os


class SDGBufferAnalyzer:
    """SDG公共交通缓冲区分析器"""
    
    def __init__(self, workspace: str = None):
        """
        初始化缓冲区分析器
        
        Args:
            workspace: 工作空间路径
        """
        if workspace:
            arcpy.env.workspace = workspace
            arcpy.env.overwriteOutput = True
    
    def clip_features(self, input_features: str, clip_boundary: str, 
                     output_features: str) -> str:
        """
        裁剪要素到边界范围内
        
        Args:
            input_features: 输入要素路径
            clip_boundary: 裁剪边界路径
            output_features: 输出要素路径
            
        Returns:
            输出要素路径
        """
        try:
            arcpy.Clip_analysis(input_features, clip_boundary, output_features, "")
            return output_features
        except arcpy.ExecuteError as e:
            raise Exception(f"要素裁剪失败: {e}")
    
    def create_buffer(self, input_features: str, output_buffer: str, 
                     distance: float, buffer_type: str = "FULL") -> str:
        """
        创建缓冲区
        
        Args:
            input_features: 输入要素路径
            output_buffer: 输出缓冲区路径
            distance: 缓冲区距离（米）
            buffer_type: 缓冲区类型（FULL/LEFT/RIGHT）
            
        Returns:
            输出缓冲区路径
        """
        try:
            arcpy.Buffer_analysis(
                input_features, output_buffer, f"{distance} Meters", 
                buffer_type, "ROUND", "ALL", "", "GEODESIC"
            )
            return output_buffer
        except arcpy.ExecuteError as e:
            raise Exception(f"缓冲区创建失败: {e}")
    
    def merge_features(self, input_features_list: List[str], 
                      output_features: str) -> str:
        """
        合并多个要素类
        
        Args:
            input_features_list: 输入要素路径列表
            output_features: 输出要素路径
            
        Returns:
            输出要素路径
        """
        try:
            input_features = ";".join(input_features_list)
            arcpy.Merge_management(input_features, output_features)
            return output_features
        except arcpy.ExecuteError as e:
            raise Exception(f"要素合并失败: {e}")
    
    def dissolve_features(self, input_features: str, output_features: str, 
                         dissolve_field: str = "") -> str:
        """
        融合要素
        
        Args:
            input_features: 输入要素路径
            output_features: 输出要素路径
            dissolve_field: 融合字段
            
        Returns:
            输出要素路径
        """
        try:
            arcpy.Dissolve_management(
                input_features, output_features, dissolve_field, 
                "", "MULTI_PART", "DISSOLVE_LINES"
            )
            return output_features
        except arcpy.ExecuteError as e:
            raise Exception(f"要素融合失败: {e}")
    
    def extract_by_mask(self, input_raster: str, mask_features: str, 
                       output_raster: str) -> str:
        """
        按掩膜提取栅格数据
        
        Args:
            input_raster: 输入栅格路径
            mask_features: 掩膜要素路径
            output_raster: 输出栅格路径
            
        Returns:
            输出栅格路径
        """
        try:
            arcpy.gp.ExtractByMask_sa(input_raster, mask_features, output_raster)
            return output_raster
        except arcpy.ExecuteError as e:
            raise Exception(f"栅格提取失败: {e}")
    
    def raster_to_point(self, input_raster: str, output_points: str, 
                       field: str = "Value") -> str:
        """
        栅格转点
        
        Args:
            input_raster: 输入栅格路径
            output_points: 输出点要素路径
            field: 值字段
            
        Returns:
            输出点要素路径
        """
        try:
            arcpy.RasterToPoint_conversion(input_raster, output_points, field)
            return output_points
        except arcpy.ExecuteError as e:
            raise Exception(f"栅格转点失败: {e}")
    
    def spatial_join(self, target_features: str, join_features: str,
                    output_features: str, search_radius: float = None) -> str:
        """
        空间连接分析
        
        Args:
            target_features: 目标要素路径
            join_features: 连接要素路径
            output_features: 输出要素路径
            search_radius: 搜索半径（米）
            
        Returns:
            输出要素路径
        """
        try:
            if search_radius:
                arcpy.SpatialJoin_analysis(
                    target_features, join_features, output_features,
                    "JOIN_ONE_TO_ONE", "KEEP_ALL", "",
                    "WITHIN_A_DISTANCE_GEODESIC", f"{search_radius} Meters", ""
                )
            else:
                arcpy.SpatialJoin_analysis(
                    target_features, join_features, output_features,
                    "JOIN_ONE_TO_ONE", "KEEP_ALL"
                )
            return output_features
        except arcpy.ExecuteError as e:
            raise Exception(f"空间连接失败: {e}")
    
    def calculate_service_area(self, bus_stops: str, tram_stops: str, 
                             railway_stations: str, ferry_terminals: str,
                             boundary: str, output_valid_area: str) -> str:
        """
        计算公共交通有效服务区域
        
        Args:
            bus_stops: 公交站点数据
            tram_stops: 有轨电车站点数据  
            railway_stations: 火车站数据
            ferry_terminals: 轮渡站点数据
            boundary: 研究区域边界
            output_valid_area: 输出有效区域路径
            
        Returns:
            有效服务区域路径
        """
        # 裁剪各类交通站点
        bus_clip = self.clip_features(bus_stops, boundary, "bus_stops_clip.shp")
        tram_clip = self.clip_features(tram_stops, boundary, "tram_stops_clip.shp")
        railway_clip = self.clip_features(railway_stations, boundary, "railway_clip.shp")
        ferry_clip = self.clip_features(ferry_terminals, boundary, "ferry_clip.shp")
        
        # 创建缓冲区
        bus_buffer = self.create_buffer(bus_clip, "bus_500m_buffer.shp", 500)
        other_buffer = self.create_buffer(
            [tram_clip, railway_clip, ferry_clip], 
            "other_1000m_buffer.shp", 1000
        )
        
        # 合并缓冲区
        merged_buffer = self.merge_features(
            [bus_buffer, other_buffer], "merged_buffer.shp"
        )
        
        # 裁剪到研究区域
        clipped_buffer = self.clip_features(
            merged_buffer, boundary, "clipped_buffer.shp"
        )
        
        # 融合最终有效区域
        valid_area = self.dissolve_features(
            clipped_buffer, output_valid_area
        )
        
        return valid_area