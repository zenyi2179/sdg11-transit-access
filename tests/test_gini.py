"""
基尼系数计算测试模块

功能：
- 测试GiniCalculator类的各种功能
- 验证基尼系数计算的正确性
"""

import unittest
import tempfile
import os
import csv
import numpy as np

# 添加src目录到Python路径
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from pt_access.gini import GiniCalculator


class TestGiniCalculator(unittest.TestCase):
    """基尼系数计算器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.calculator = GiniCalculator()
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建测试数据
        self.test_data = [
            ['1', '1001', '500.0', '2', '1', '0', '3'],
            ['2', '1002', '300.0', '1', '0', '1', '2'], 
            ['3', '1003', '200.0', '0', '0', '0', '0'],
            ['4', '1004', '400.0', '3', '0', '0', '3'],
            ['5', '1005', '600.0', '1', '1', '1', '3']
        ]
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_calculate_basic_stats(self):
        """测试基本统计计算"""
        stats = self.calculator.calculate_basic_stats(self.test_data)
        
        # 验证统计结果
        self.assertIn('total_population', stats)
        self.assertIn('valid_population', stats)
        self.assertIn('population_ratio', stats)
        
        # 验证数值范围
        self.assertGreater(stats['total_population'], 0)
        self.assertGreaterEqual(stats['population_ratio'], 0)
        self.assertLessEqual(stats['population_ratio'], 1)
    
    def test_prepare_gini_data(self):
        """测试基尼数据准备"""
        summary_table = self.calculator.prepare_gini_data(self.test_data)
        
        # 验证数据格式
        self.assertIsInstance(summary_table, np.ndarray)
        self.assertGreater(summary_table.shape[0], 0)
        self.assertEqual(summary_table.shape[1], 7)  # 7列数据
    
    def test_calculate_gini_coefficient(self):
        """测试基尼系数计算"""
        summary_table = self.calculator.prepare_gini_data(self.test_data)
        gini_coefficient, results = self.calculator.calculate_gini_coefficient(summary_table)
        
        # 验证基尼系数范围
        self.assertGreaterEqual(gini_coefficient, 0)
        self.assertLessEqual(gini_coefficient, 1)
        
        # 验证结果字典包含必要键
        self.assertIn('gini_coefficient', results)
        self.assertIn('cumulative_sum', results)
        self.assertIn('pw_product', results)
    
    def test_gini_with_perfect_equality(self):
        """测试完全平等情况下的基尼系数"""
        # 创建完全平等的数据
        equal_data = [
            ['1', '1001', '100.0', '1', '0', '0', '1'],
            ['2', '1002', '100.0', '1', '0', '0', '1'],
            ['3', '1003', '100.0', '1', '0', '0', '1']
        ]
        
        summary_table = self.calculator.prepare_gini_data(equal_data)
        gini_coefficient, _ = self.calculator.calculate_gini_coefficient(summary_table)
        
        # 完全平等时基尼系数应该接近0
        self.assertAlmostEqual(gini_coefficient, 0, places=2)
    
    def test_gini_with_perfect_inequality(self):
        """测试完全不平等情况下的基尼系数"""
        # 创建完全不平等的数据
        unequal_data = [
            ['1', '1001', '100.0', '0', '0', '0', '0'],
            ['2', '1002', '100.0', '0', '0', '0', '0'], 
            ['3', '1003', '100.0', '3', '1', '1', '5']
        ]
        
        summary_table = self.calculator.prepare_gini_data(unequal_data)
        gini_coefficient, _ = self.calculator.calculate_gini_coefficient(summary_table)
        
        # 完全不平等时基尼系数应该接近1
        self.assertGreater(gini_coefficient, 0.5)
    
    def test_generate_gini_report(self):
        """测试基尼报告生成"""
        # 创建测试CSV文件
        test_csv = os.path.join(self.temp_dir, "test_data.csv")
        with open(test_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['fid', 'pointid', 'population', 'bus', 'railway', 'tram', 'gather'])
            writer.writerows(self.test_data)
        
        # 生成报告
        output_file = os.path.join(self.temp_dir, "test_report.xlsx")
        results = self.calculator.generate_gini_report(test_csv, output_file)
        
        # 验证结果
        self.assertIn('basic_statistics', results)
        self.assertIn('gini_coefficient', results)
        self.assertIn('gini_details', results)
        
        # 验证文件生成
        self.assertTrue(os.path.exists(output_file))


if __name__ == '__main__':
    unittest.main()