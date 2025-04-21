#!/bin/bash
# 示例脚本 - 展示不同使用方法

# 创建目录
mkdir -p examples/output

# 示例1: 简单下载并转换一个网站
echo "### 示例1: 简单下载并转换网站 ###"
python -m website_converter.cli --url https://example.com --output examples/output/example_com

# 示例2: 限制处理文件数量（测试用）
echo "### 示例2: 限制处理文件数量 ###"
python -m website_converter.cli --url https://example.com --output examples/output/example_limited --limit 10

# 示例3: 使用自定义标题
echo "### 示例3: 自定义标题 ###"
python -m website_converter.cli --url https://example.com --output examples/output/example_titled --title "我的示例网站镜像"

# 示例4: 指定下载深度
echo "### 示例4: 指定下载深度 ###"
python -m website_converter.cli --url https://example.com --output examples/output/example_depth --depth 3

# 示例5: 启动HTTP服务器
echo "### 示例5: 启动HTTP服务器 ###"
python -m website_converter.cli --url https://example.com --output examples/output/example_server --server --port 8888

# 示例6: 只处理现有文件，跳过下载
echo "### 示例6: 跳过下载，只处理现有文件 ###"
python -m website_converter.cli --url https://example.com --output examples/output/example_no_download --download-dir examples/output/example_com --no-download

# 清理
echo "如需清理示例，请运行: rm -rf examples/output"
