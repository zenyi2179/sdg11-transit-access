"""
工具函数测试模块

功能：
- 测试各种工具函数的正确性
- 验证数据验证和文件处理功能
"""

import unittest
import tempfile
import os
import pandas as pd
import numpy as np

# 添加src目录到Python路径
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from pt_access.utils import DataValidator, FileProcessor


class TestDataValidator(unittest.TestCase):
    """数据验证器测试类"""
    
    def test_validate_coordinate(self):
        """测试坐标验证"""
        # 测试有效坐标
        self.assertTrue(DataValidator.validate_coordinate(116.0, 39.0))
        self.assertTrue(DataValidator.validate_coordinate(-74.0, 40.0))
        self.assertTrue(DataValidator.validate_coordinate(0.0, 0.0))
        
        # 测试无效坐标
        self.assertFalse(DataValidator.validate_coordinate(200.0, 39.0))  # 经度超出范围
        self.assertFalse(DataValidator.validate_coordinate(116.0, 100.0))  # 纬度超出范围
        self.assertFalse(DataValidator.validate_coordinate(-181.0, 39.0))  # 经度超出范围
    
    def test_validate_population_data(self):
        """测试人口数据验证"""
        # 测试有效人口数据
        self.assertTrue(DataValidator.validate_population_data(1000.0))
        self.assertTrue(DataValidator.validate_population_data(0.0))
        self.assertTrue(DataValidator.validate_population_data(1e6))
        
        # 测试无效人口数据
        self.assertFalse(DataValidator.validate_population_data(-100.0))
        self.assertFalse(DataValidator.validate_population_data(np.nan))
    
    def test_clean_dataframe(self):
        """测试DataFrame清理"""
        # 创建测试DataFrame
        test_data = {
            'id': [1, 2, 3, 4, 5],
            'name': ['A', 'B', None, 'D', 'E'],
            'population': [100, 200, 300, None, 500],
            'empty_col': [None, None, None, None, None]
        }
        df = pd.DataFrame(test_data)
        
        # 清理数据
        cleaned_df = DataValidator.clean_dataframe(
            df, 
            drop_na_columns=['population']
        )
        
        # 验证清理结果
        self.assertEqual(len(cleaned_df), 4)  # 删除包含空值的行
        self.assertNotIn('empty_col', cleaned_df.columns)  # 删除全空列
        self.assertFalse(cleaned_df['population'].isna().any())  # 确保population列无空值


class TestFileProcessor(unittest.TestCase):
    """文件处理器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_read_write_csv_data(self):
        """测试CSV数据读写"""
        test_data = [
            ['id', 'name', 'value'],
            ['1', 'A', '100'],
            ['2', 'B', '200'],
            ['3', 'C', '300']
        ]
        
        test_file = os.path.join(self.temp_dir, "test.csv")
        
        # 写入数据
        result_write = FileProcessor.write_csv_data(
            test_data[1:],  # 不包含标题
            test_file,
            headers=test_data[0]
        )
        self.assertTrue(result_write)
        
        # 读取数据
        read_data = FileProcessor.read_csv_data(test_file)
        self.assertEqual(len(read_data), 3)  # 3行数据
        self.assertEqual(read_data[0], ['1', 'A', '100'])
    
    def test_get_file_list(self):
        """测试文件列表获取"""
        # 创建测试文件
        test_files = ['test1.txt', 'test2.csv', 'test3.xlsx']
        for file in test_files:
            with open(os.path.join(self.temp_dir, file), 'w') as f:
                f.write("test")
        
        # 获取所有文件
        all_files = FileProcessor.get_file_list(self.temp_dir)
        self.assertEqual(len(all_files), 3)
        
        # 获取特定扩展名文件
        csv_files = FileProcessor.get_file_list(self.temp_dir, '.csv')
        self.assertEqual(len(csv_files), 1)
        self.assertTrue(csv_files[0].endswith('.csv'))
    
    def test_backup_file(self):
        """测试文件备份"""
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("original content")
        
        # 备份文件
        backup_path = FileProcessor.backup_file(test_file)
        self.assertTrue(os.path.exists(backup_path))
        
        # 验证备份内容
        with open(backup_path, 'r') as f:
            content = f.read()
        self.assertEqual(content, "original content")
    
    def test_validate_file_path(self):
        """测试文件路径验证"""
        # 测试有效路径
        valid_file = os.path.join(self.temp_dir, "valid.txt")
        with open(valid_file, 'w') as f:
            f.write("test")
        
        self.assertTrue(FileProcessor.validate_file_path(valid_file))
        
        # 测试无效路径
        self.assertFalse(FileProcessor.validate_file_path(""))
        self.assertFalse(FileProcessor.validate_file_path("/nonexistent/path.txt"))


if __name__ == '__main__':
    unittest.main()