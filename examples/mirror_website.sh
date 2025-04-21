#!/bin/bash
# 使用wget递归下载整个网站

# 设置默认值
URL=${1:-"https://learn.lianglianglee.com/"}
OUTPUT_DIR=${2:-"learn.lianglianglee.com_httrack"}
DEPTH=${3:-3}
WAIT_TIME=${4:-"3-8"}  # 格式: "min-max"

# 参数验证
if [ -z "$URL" ]; then
    echo "请提供网站URL"
    echo "用法: $0 [URL] [输出目录] [最大递归深度=3] [等待时间范围=\"3-8\"]"
    exit 1
fi

echo "=== 网站镜像工具 ==="
echo "目标网站: $URL"
echo "输出目录: $OUTPUT_DIR"
echo "最大递归深度: $DEPTH"
echo "请求间隔时间(秒): $WAIT_TIME"
echo "====================\n"

# 解析等待时间范围
MIN_WAIT=$(echo $WAIT_TIME | cut -d'-' -f1)
MAX_WAIT=$(echo $WAIT_TIME | cut -d'-' -f2)
WAIT_RANGE=$((MAX_WAIT - MIN_WAIT))

# 计算随机等待时间
RANDOM_WAIT=""
if [ $WAIT_RANGE -gt 0 ]; then
    RANDOM_WAIT="--random-wait --wait=$MIN_WAIT"
else
    RANDOM_WAIT="--wait=$MIN_WAIT"
fi

# 激活虚拟环境（如果有）
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "开始下载网站: $URL"
echo "这可能需要一段时间，具体取决于网站大小..."
echo "下载过程中请勿关闭终端"

# 使用wget递归下载网站
wget --recursive \
     --level=$DEPTH \
     --no-clobber \
     --page-requisites \
     --html-extension \
     --convert-links \
     --restrict-file-names=windows \
     --domains $(echo $URL | awk -F/ '{print $3}') \
     --no-parent \
     $RANDOM_WAIT \
     --header="User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36" \
     --header="Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" \
     --header="Accept-Language: zh-CN,zh;q=0.9,en;q=0.8" \
     --reject "index.html?*" \
     -P "$OUTPUT_DIR" \
     $URL

echo "下载完成！文件保存在 $OUTPUT_DIR 目录中"
echo "现在可以使用 website_converter 工具来处理这些文件"
echo "示例命令:"
echo "python -m website_converter.cli --url $URL --download-dir $OUTPUT_DIR --title \"网站标题\" --verbose --server"
