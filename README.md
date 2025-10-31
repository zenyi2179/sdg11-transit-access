# SDG 11 公共交通可达性分析工具包

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://your-organization.github.io/sdg11-pt-access/)


一个用于分析联合国可持续发展目标（SDG）11.2.1指标 - 公共交通可达性的Python工具包。
本项目基于联合国可持续发展目标（Sustainable Development Goals, SDGs）中第 11 项 “可持续城市与社区” 的 11.2 指标，旨在通过地理信息系统 (GIS) 技术评估城市居民在不同公共交通设施可达范围内的人口覆盖率。 本研究利用 ArcGIS 的空间分析模型、开放街图 (OSM) 数据及人口栅格数据，实现了公共交通站点的空间缓冲区分析、人口掩膜筛选及可达性基尼系数的计算，最终生成可复现的自动化分析流程。


## 功能特性

### 🚌 公共交通可达性分析
- **缓冲区分析**: 500米（公交）和1000米（轨道交通）服务范围计算
- **人口覆盖分析**: 计算公共交通服务覆盖的人口比例
- **服务区域识别**: 识别有效的公共交通服务区域

### 📊 公平性评估
- **基尼系数计算**: 评估公共交通服务的空间公平性
- **统计分析**: 提供详细的统计报告和可视化
- **比较分析**: 支持不同城市、不同时间段的对比分析

### 🕸️ 数据获取与处理
- **网络爬虫**: 从8684网站获取公交线路和站点数据
- **坐标转换**: GCJ02到WGS84坐标系批量转换
- **数据清洗**: 自动化数据验证和清理

### 🔧 技术特点
- **模块化设计**: 高度可扩展的模块化架构
- **类型注解**: 完整的Python类型提示
- **单元测试**: 全面的测试覆盖
- **文档完善**: 详细的API文档和使用示例

## 安装

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/your-organization/sdg11-pt-access.git
cd sdg11-pt-access

# 安装依赖
pip install -r requirements.txt

# 开发模式安装
pip install -e .
```

### 开发环境安装

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 安装预提交钩子
pre-commit install
```

## 快速开始

### 基本使用

```python
from pt_access import SDGBufferAnalyzer, GiniCalculator

# 初始化分析器
analyzer = SDGBufferAnalyzer()

# 计算公共交通服务区域
valid_area = analyzer.calculate_service_area(
    bus_stops="data/raw/bus_stops.shp",
    tram_stops="data/raw/tram_stops.shp", 
    boundary="data/raw/boundary.shp",
    output_valid_area="output/valid_area.shp"
)

# 计算基尼系数
gini_calc = GiniCalculator()
results = gini_calc.generate_gini_report(
    "data/analysis_results.csv",
    "output/gini_report.xlsx"
)

print(f"基尼系数: {results['gini_coefficient']:.4f}")
```



### 命令行工具

```bash
# 下载公交数据
python scripts/download_bus_data.py wuhan 武汉 --api-key YOUR_API_KEY

# 处理人口数据  
python scripts/process_population.py \
    --population-raster data/raw/population.tif \
    --boundary data/raw/boundary.shp \
    --valid-area output/valid_area.shp

# 坐标转换
python scripts/coordinate_conversion.py input_coordinates.xlsx
```



## 项目结构

```text
sdg11-pt-access/
├── src/                    # 源代码
│   └── pt_access/         # 主包
│       ├── __init__.py
│       ├── buffer.py      # 缓冲区分析
│       ├── gini.py        # 基尼系数计算
│       ├── crawlers.py    # 网络爬虫
│       ├── coordinate.py  # 坐标转换
│       └── utils.py       # 工具函数
├── scripts/               # 可执行脚本
│   ├── download_bus_data.py
│   ├── process_population.py
│   └── coordinate_conversion.py
├── tests/                 # 单元测试
│   ├── test_buffer.py
│   ├── test_gini.py
│   └── test_utils.py
├── data/                  # 数据目录
│   ├── raw/              # 原始数据
│   ├── interim/          # 中间数据
│   └── final/            # 最终结果
├── docs/                  # 文档
├── notebooks/             # Jupyter笔记本
├── requirements.txt       # 生产依赖
├── requirements-dev.txt   # 开发依赖
└── setup.py              # 包配置
```



## 数据要求

### 输入数据

- **公共交通站点**: Shapefile格式的点数据
- **人口栅格**: GeoTIFF格式的人口密度数据
- **研究边界**: Shapefile格式的多边形边界
- **公交线路数据**: 可通过爬虫自动获取

### 输出数据

- **服务区域**: 有效的公共交通服务范围
- **人口覆盖**: 服务范围内的人口统计
- **基尼报告**: 公平性评估报告
- **可视化结果**: 各种分析图表

## 配置

在 `config.py` 中配置项目参数：

```python
from pt_access.config import Config

# 设置数据路径
Config.TRAFFIC_DATA_PATHS['bus_stops'] = "your/path/to/bus_stops.shp"

# 配置API密钥
import os
os.environ['GAODE_MAP_API_KEY'] = 'your_api_key_here'
```



## 开发指南

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_buffer.py

# 生成测试覆盖率报告
pytest --cov=pt_access tests/
```



### 代码规范

```bash
# 代码格式化
black src/ tests/

# 代码检查
flake8 src/ tests/

# 类型检查
mypy src/
```



## 贡献指南

我们欢迎各种形式的贡献！请参阅 [CONTRIBUTING.md](https://contributing.md/) 了解详细信息。

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](https://license/) 文件。

## 引用

如果您在研究中使用了本工具包，请引用：

```bibtex
@software{sdg11_pt_access,
  title = {SDG 11 Public Transport Accessibility Analysis Toolkit},
  author = {SDG Research Team},
  year = {2023},
  url = {https://github.com/your-organization/sdg11-pt-access}
}
```



## 支持

- 📚 [文档](https://your-organization.github.io/sdg11-pt-access/)
- 🐛 [问题报告](https://github.com/your-organization/sdg11-pt-access/issues)
- 💬 [讨论区](https://github.com/your-organization/sdg11-pt-access/discussions)

## 致谢

感谢以下项目的支持：

- [ArcGIS](https://www.arcgis.com/) - 空间分析平台
- [高德地图API](https://lbs.amap.com/) - 地理编码服务
- [8684公交网](https://www.8684.cn/) - 公交数据源


