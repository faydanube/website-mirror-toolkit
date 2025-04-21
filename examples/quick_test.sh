#!/bin/bash
# 使用自创测试文件验证网站镜像工具功能

echo "=== 开始测试 ==="
echo "创建测试文件..."

# 设置变量
TEST_DIR="test_samples"

# 清理并创建测试目录
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR/articles"
mkdir -p "$TEST_DIR/tutorials"

# 创建测试文件，确保UTF-8编码和正确内容
cat > "$TEST_DIR/index.html" << EOF
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>测试站点首页</title>
</head>
<body>
  <h1>测试站点首页</h1>
  <p>这是一个测试站点，用于验证网站镜像工具的功能。</p>
  <ul>
    <li><a href="articles/article1.html">测试文章一</a></li>
    <li><a href="articles/article2.html">测试文章二</a></li>
    <li><a href="tutorials/tutorial1.html">教程一</a></li>
    <li><a href="tutorials/tutorial2.html">教程二</a></li>
  </ul>
</body>
</html>
EOF

cat > "$TEST_DIR/articles/article1.html" << EOF
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>测试文章一</title>
</head>
<body>
  <h1>测试文章一</h1>
  <p>这是第一篇测试文章，包含了<strong>加粗文本</strong>和<em>斜体文本</em>。</p>
  <p>这里有一个链接：<a href="../index.html">返回首页</a></p>
  <p>这里是一些中文内容，测试UTF-8编码是否正常。</p>
</body>
</html>
EOF

cat > "$TEST_DIR/articles/article2.html" << EOF
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>测试文章二</title>
</head>
<body>
  <h1>测试文章二</h1>
  <p>这是第二篇测试文章，包含了一个表格：</p>
  <table border="1">
    <tr>
      <th>标题一</th>
      <th>标题二</th>
    </tr>
    <tr>
      <td>单元格1</td>
      <td>单元格2</td>
    </tr>
  </table>
  <p>这里有一个链接：<a href="../index.html">返回首页</a></p>
</body>
</html>
EOF

cat > "$TEST_DIR/tutorials/tutorial1.html" << EOF
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>教程一：基础知识</title>
</head>
<body>
  <h1>教程一：基础知识</h1>
  <p>这是第一个教程，介绍一些基础知识。</p>
  <h2>第一部分</h2>
  <p>基础知识的第一部分内容。</p>
  <h2>第二部分</h2>
  <p>基础知识的第二部分内容。</p>
  <p><a href="../index.html">返回首页</a></p>
</body>
</html>
EOF

cat > "$TEST_DIR/tutorials/tutorial2.html" << EOF
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>教程二：高级知识</title>
</head>
<body>
  <h1>教程二：高级知识</h1>
  <p>这是第二个教程，介绍一些高级知识。</p>
  <ul>
    <li>高级知识点一</li>
    <li>高级知识点二</li>
    <li>高级知识点三</li>
  </ul>
  <p><a href="../index.html">返回首页</a></p>
</body>
</html>
EOF

echo "测试文件创建完成。共5个HTML文件"
echo "准备处理文件..."

# 运行转换器并启动服务器
python -m website_converter.cli \
    --url "https://testsite.com/" \
    --download-dir "$TEST_DIR" \
    --no-download \
    --file-types all \
    --title "测试站点" \
    --verbose \
    --server \
    --port 8888

echo "测试完成，请查看浏览器中的结果"
