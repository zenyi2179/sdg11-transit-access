"""
项目安装配置

功能：
- 定义Python包元数据
- 配置包依赖和入口点
- 支持pip安装
"""

from setuptools import setup, find_packages
import os

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sdg11-pt-access",
    version="1.0.0",
    author="SDG Research Team",
    author_email="research@example.com",
    description="SDG 11 公共交通可达性分析工具包",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-organization/sdg11-pt-access",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "flake8>=3.9",
            "black>=21.0",
            "mypy>=0.9",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "myst-parser>=0.15",
        ],
    },
    entry_points={
        "console_scripts": [
            "sdg-buffer=pt_access.cli:buffer_analysis",
            "sdg-gini=pt_access.cli:gini_analysis", 
            "sdg-crawl=pt_access.cli:crawl_bus_data",
        ],
    },
    include_package_data=True,
    package_data={
        "pt_access": [
            "data/*.json",
            "config/*.yml",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/your-organization/sdg11-pt-access/issues",
        "Source": "https://github.com/your-organization/sdg11-pt-access",
        "Documentation": "https://your-organization.github.io/sdg11-pt-access/",
    },
)