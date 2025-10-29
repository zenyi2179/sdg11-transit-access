"""
缓冲区分析测试模块

功能：
- 测试SDGBufferAnalyzer类的各种功能
- 验证空间分析结果的正确性
"""

import unittest
import os
import tempfile
import arcpy
from unittest.mock import Mock, patch

# 添加src目录到Python路径
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from pt_access.buffer import SDGBufferAnalyzer
from pt_access.utils import FileProcessor


class TestSDGBufferAnalyzer(unittest.TestCase):
    """SDG缓冲区分析器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.analyzer = SDGBufferAnalyzer(self.temp_dir)
        
        # 创建测试数据
        self.test_points = os.path.join(self.temp_dir, "test_points.shp")
        self.test_boundary = os.path.join(self.temp_dir, "test_boundary.shp")
        
        # 创建测试点要素
        arcpy.CreateFeatureclass_management(
            self.temp_dir, "test_points.shp", "POINT"
        )
        arcpy.AddField_management(self.test_points, "Name", "TEXT")
        
        # 创建测试边界
        arcpy.CreateFeatureclass_management(
            self.temp_dir, "test_boundary.shp", "POLYGON"
        )
    
    def tearDown(self):
        """测试后清理"""
        # 清理临时文件
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('arcpy.Clip_analysis')
    def test_clip_features(self, mock_clip):
        """测试要素裁剪功能"""
        # 设置mock返回值
        mock_clip.return_value = None
        
        # 执行测试
        result = self.analyzer.clip_features(
            "input.shp", "boundary.shp", "output.shp"
        )
        
        # 验证结果
        self.assertEqual(result, "output.shp")
        mock_clip.assert_called_once()
    
    @patch('arcpy.Buffer_analysis')
    def test_create_buffer(self, mock_buffer):
        """测试缓冲区创建功能"""
        # 设置mock返回值
        mock_buffer.return_value = None
        
        # 执行测试
        result = self.analyzer.create_buffer(
            "input.shp", "output.shp", 500
        )
        
        # 验证结果
        self.assertEqual(result, "output.shp")
        mock_buffer.assert_called_once()
    
    @patch('arcpy.Merge_management')
    def test_merge_features(self, mock_merge):
        """测试要素合并功能"""
        # 设置mock返回值
        mock_merge.return_value = None
        
        # 执行测试
        input_list = ["input1.shp", "input2.shp"]
        result = self.analyzer.merge_features(input_list, "output.shp")
        
        # 验证结果
        self.assertEqual(result, "output.shp")
        mock_merge.assert_called_once()
    
    def test_analyzer_initialization(self):
        """测试分析器初始化"""
        analyzer = SDGBufferAnalyzer("/test/workspace")
        self.assertIsNotNone(analyzer)
    
    def test_invalid_inputs(self):
        """测试无效输入处理"""
        with self.assertRaises(Exception):
            self.analyzer.clip_features("", "", "")


class TestFileProcessor(unittest.TestCase):
    """文件处理器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_ensure_directory(self):
        """测试目录创建功能"""
        test_dir = os.path.join(self.temp_dir, "test_subdir")
        
        # 测试目录创建
        result = FileProcessor.ensure_directory(test_dir)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(test_dir))
    
    def test_validate_file_path(self):
        """测试文件路径验证"""
        # 测试有效路径
        valid_path = os.path.join(self.temp_dir, "test.txt")
        with open(valid_path, 'w') as f:
            f.write("test")
        
        self.assertTrue(FileProcessor.validate_file_path(valid_path))
        
        # 测试无效路径
        self.assertFalse(FileProcessor.validate_file_path(""))
        self.assertFalse(FileProcessor.validate_file_path("/nonexistent/path.txt"))


if __name__ == '__main__':
    unittest.main()