# 网站镜像工具开发规则

本文档总结了在开发和使用网站镜像工具时常见的问题和解决方案，作为编写和使用相关工具的指南。

## 1. 编码处理规则

### 规则1.1: 始终使用二进制模式读取原始文件

**问题**: 不同网站使用不同的编码，直接使用特定编码读取文件常导致乱码。

**解决方案**: 总是先以二进制模式读取文件，然后尝试多种编码进行解码。

```python
# 正确的做法
with open(file_path, 'rb') as f:
    raw_content = f.read()

# 尝试多种编码
for encoding in ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5', 'iso-8859-1']:
    try:
        content = raw_content.decode(encoding)
        detected_encoding = encoding
        break
    except UnicodeDecodeError:
        continue
```

### 规则1.2: 处理UTF-8 BOM标记

**问题**: 一些UTF-8文件包含BOM标记，可能导致解析问题。

**解决方案**: 检测并处理BOM标记。

```python
# 检测UTF-8 BOM
if raw_content.startswith(b'\xef\xbb\xbf'):  # UTF-8 BOM
    content = raw_content[3:].decode('utf-8')
    detected_encoding = 'utf-8-sig'
```

### 规则1.3: 统一输出文件编码为UTF-8

**问题**: 编码不一致导致后续处理出现问题。

**解决方案**: 所有输出文件一律使用UTF-8编码，并添加明确的编码声明。

```python
# 添加或修复HTML编码声明
html_content = re.sub(
    r'<meta[^>]*charset=["\']?([^"\'>]*)["\']?[^>]*>',
    f'<meta charset="utf-8">',
    html_content
)

# 如果没有编码声明，添加一个
if 'charset=' not in html_content and '<head' in html_content:
    html_content = html_content.replace('<head>', '<head>\n    <meta charset="utf-8">')

# 写入文件时明确指定UTF-8编码
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(content)
```

## 2. 文件路径处理规则

### 规则2.1: 使用域名目录组织文件

**问题**: 不正确的文件路径导致链接失效。

**解决方案**: 始终将所有文件放在以域名命名的子目录下，保持与原站点相同的相对路径。

```python
# 正确的输出路径应该是：
output_path = os.path.join(self.output_dir, self.domain, rel_path)
```

### 规则2.2: 总是确保目标目录存在

**问题**: 写入文件前目录不存在导致失败。

**解决方案**: 每次写入文件前先确保目录存在。

```python
# 确保输出目录存在
os.makedirs(os.path.dirname(output_path), exist_ok=True)
```

## 3. HTML内容处理规则

### 规则3.1: 对不完整的HTML添加基本结构

**问题**: 一些HTML文件可能不包含完整的HTML结构，导致渲染问题。

**解决方案**: 检测并为不完整的HTML添加基本结构。

```python
# 检查HTML是否完整
if "<html" not in html_content.lower():
    # 提取或创建标题
    title = extract_title_or_create_from_filename(file_path)

    # 创建完整HTML结构
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <link rel="stylesheet" href="/{domain}/static/index.css">
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="content">
            {html_content}
        </div>
    </div>
</body>
</html>"""
```

### 规则3.2: 智能提取标题

**问题**: 页面标题对用户导航至关重要，但不一定能直接获取。

**解决方案**: 尝试多种方法提取标题，优先级：`<title>` > `<h1>` > 文件名。

```python
# 尝试提取标题
title_match = re.search(r'<title>(.*?)</title>', content)
if title_match:
    title = title_match.group(1)
else:
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content)
    if h1_match:
        title = h1_match.group(1)
    else:
        # 从文件名生成标题
        filename = os.path.basename(file_path)
        title = os.path.splitext(filename)[0].replace('-', ' ').replace('_', ' ').title()
```

## 4. 链接修复规则

### 规则4.1: 确保所有内部链接包含域名前缀

**问题**: 内部链接没有域名前缀导致链接失效。

**解决方案**: 为所有内部链接添加域名前缀。

```python
# 将相对链接转换为带域名的链接
content = re.sub(
    r'(href|src)=[\'"](?!http|https|ftp|mailto|tel|#|/|javascript)([^\'"]+)[\'"]',
    rf'\1="/{self.domain}/\2"',
    content
)

# 将根路径链接转换为带域名的链接
content = re.sub(
    r'(href|src)=[\'"]/((?!{domain}).+?)[\'"]'.format(domain=re.escape(self.domain)),
    rf'\1="/{self.domain}/\2"',
    content
)
```

### 规则4.2: 确保链接扩展名一致性

**问题**: Markdown链接和一些特殊链接的扩展名需要一致处理。

**解决方案**: 统一处理链接扩展名。

```python
# 把.md链接转换为.html
url = re.sub(r'\.md($|\?|#)', r'.html\1', url)

# 对没有扩展名的URL添加.html
if not re.search(r'\.[a-zA-Z0-9]+($|\?|#)', url) and not url.endswith('/'):
    url = url + '.html'
```

## 5. 测试策略规则

### 规则5.1: 使用自创内容进行初步测试

**问题**: 依赖外部网站内容进行测试容易受网站变化影响，增加测试难度。

**解决方案**: 创建包含所有可能元素的测试文件集进行初步功能验证。

```bash
# 创建测试文件目录结构
mkdir -p test_samples/{分类1,分类2}

# 创建各种类型的测试文件，确保包含：
# 1. 完整的HTML结构
# 2. 不同的编码（明确声明UTF-8）
# 3. 各种链接类型（相对路径、绝对路径）
# 4. 特殊HTML元素（表格、列表等）
# 5. 中文内容（测试编码）
```

### 规则5.2: 分阶段测试

**问题**: 一次性测试全部功能难以定位具体问题。

**解决方案**: 分阶段测试不同功能点。

1. 先测试基本文件读写、编码处理
2. 再测试HTML修复和链接处理
3. 最后测试完整流程和UI呈现

### 规则5.3: 详细的日志输出

**问题**: 没有足够的日志难以诊断问题。

**解决方案**: 添加详细的日志，特别是关键步骤的输入输出信息。

```python
# 添加文件处理日志
print(f"处理文件: {file_path} (编码: {detected_encoding})")

# 添加链接修复日志
if verbose:
    print(f"修复链接: {original_url} -> {fixed_url}")

# 添加关键处理步骤日志
print(f"找到{len(files)}个文件，分为{len(categories)}个分类")
```

## 6. 网站下载规则

### 规则6.1: 使用正确的HTTP头

**问题**: 不正确的HTTP头可能导致获取不到正确的内容或编码。

**解决方案**: 使用合适的User-Agent和Accept头。

```bash
wget --header="User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" \
     --header="Accept: text/html,application/xhtml+xml,application/xml;q=0.9" \
     --header="Accept-Language: zh-CN,zh;q=0.9,en;q=0.8" \
     --header="Accept-Encoding: gzip, deflate" \
     -O output.html "https://example.com/"
```

### 规则6.2: 使用随机延迟避免被封

**问题**: 快速连续请求可能触发网站的反爬虫机制。

**解决方案**: 添加随机延迟。

```bash
# 在请求前添加随机延迟
sleep_time=$(( RANDOM % 5 + 3 ))  # 3-7秒随机延迟
sleep $sleep_time

# 在wget中使用内置的随机等待
wget --random-wait --wait=3 ...
```

## 总结

以上规则覆盖了网站镜像工具开发中最常见的问题和解决方案。遵循这些规则，可以大大提高工具的稳定性和成功率。在实际应用中，根据具体网站的特点，可能需要进一步调整和优化这些规则。

在处理新的网站镜像任务时，建议按照以下步骤操作：

1. 先用少量测试页面验证基本功能
2. 解决可能的编码和路径问题
3. 逐步扩大测试范围
4. 最后进行完整镜像
