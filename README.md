# 网站镜像工具包 - Website Mirror Toolkit

这是一个强大的网站镜像工具包，可以将网站内容（特别是包含Markdown文件的网站）转换为本地可浏览的HTML网站。

## 主要功能

- **网站下载**: 使用HTTrack下载整个网站内容
- **Markdown转HTML**: 自动将所有`.md`文件转换为美观的HTML格式
- **链接修复**: 智能修复HTML文件中的链接，确保能在本地正常访问
- **导航首页**: 自动创建美观的导航首页，方便浏览所有内容
- **内置HTTP服务器**: 可选的内置HTTP服务器，方便快速预览

## 系统要求

- Python 3.6+
- HTTrack (网站下载工具)

## 安装方法

### 1. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装HTTrack（仅在需要下载网站时必须）
# Linux
sudo apt-get install httrack
# macOS
brew install httrack
# Windows
# 从 http://www.httrack.com/page/2/ 下载安装包
```

### 2. 开发环境安装

```bash
# 开发模式安装
pip install -e .
```

## 使用方法

### 基本用法

```bash
# 直接运行模块
python -m website_converter.cli --url https://example.com

# 或使用安装后的命令
website-converter --url https://example.com
```

### 常用选项

- `--url`, `-u`: 要下载的网站URL
- `--output`, `-o`: 输出目录，默认为：域名_html
- `--download-dir`, `-d`: 下载目录，默认为：域名_httrack
- `--no-download`: 跳过下载步骤，仅处理已下载的内容
- `--server`: 启动内置HTTP服务器（默认不启动）
- `--port`, `-p`: HTTP服务器端口（默认: 8080）
- `--title`: 网站标题（默认: 网站离线镜像）

### 使用示例

<!-- markdownlint-disable MD029 -->
1. 下载并转换网站:
<!-- markdownlint-restore -->

```bash
python -m website_converter.cli --url https://learn.lianglianglee.com
```

<!-- markdownlint-disable MD029 -->
2. 只转换已下载的内容:
<!-- markdownlint-restore -->

```bash
python -m website_converter.cli --url https://example.com --no-download --download-dir example_com_httrack
```

<!-- markdownlint-disable MD029 -->
3. 使用内置HTTP服务器:
<!-- markdownlint-restore -->

```bash
python -m website_converter.cli --url https://example.com --server
```

<!-- markdownlint-disable MD029 -->
4. 使用自己的HTTP服务器:
<!-- markdownlint-restore -->

```bash
# 只转换网站，不启动服务器
python -m website_converter.cli --url https://example.com

# 然后使用任何HTTP服务器访问生成的文件
cd example.com_html
python -m http.server 8080  # 或使用nginx、Apache等
```

## 常见问题

### 权限问题

如果遇到权限错误，请确保您有足够的权限读取输入目录和写入输出目录。

### 链接错误

如果访问某些页面时链接不工作，可能是因为原始网站使用了特殊的URL结构。

### 服务器启动失败

如果HTTP服务器启动失败，请检查指定的端口是否已被占用，或尝试使用`--port`参数指定其他端口。

### Markdown转换失败

如果某些Markdown文件转换失败，可能是因为文件格式不规范或使用了特殊语法。
