#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心功能模块

实现网站下载、转换和处理的主要功能
"""

import os
import sys
import re
import shutil
import time
import subprocess
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
import socket
import http.server
import socketserver
import webbrowser
import threading

try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
    print("警告: 未安装markdown库，将无法转换Markdown文件。请使用pip安装: pip install markdown")


class WebsiteConverter:
    """网站转换器类，处理网站下载和转换流程"""

    def __init__(self, args):
        """初始化转换器，设置参数和目录"""
        self.args = args
        self.url = args.url
        self.domain = self._get_domain_from_url(args.url)

        # 设置目录
        self.download_dir = args.download_dir or f"{self.domain}_httrack"
        self.output_dir = args.output or f"{self.domain}_html"

        # 内部状态
        self.processed_count = 0
        self.total_count = 0
        self.start_time = time.time()

    def run(self):
        """运行完整的转换流程"""
        print(f"开始处理网站: {self.domain}")
        print(f"下载目录: {self.download_dir}")
        print(f"输出目录: {self.output_dir}")

        # 步骤1: 如果指定URL且未禁用下载，则下载网站
        if self.url and not self.args.no_download:
            if not self._download_website():
                print("下载失败，程序终止")
                return False

        # 步骤2: 处理文件
        if not self._process_files():
            print("处理文件失败，程序终止")
            return False

        # 步骤3: 创建索引页面
        if not self._create_index_html():
            print("创建索引页面失败，程序终止")
            return False

        # 步骤4: 如果需要，启动HTTP服务器
        if self.args.server:
            self._start_http_server()

        print(f"\n处理完成! 共处理 {self.processed_count} 个文件")
        print(f"总耗时: {time.time() - self.start_time:.2f} 秒")
        print(f"输出目录: {self.output_dir}")

        return True

    def _get_domain_from_url(self, url):
        """从URL中提取域名"""
        if not url:
            return "local_content"

        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        return domain

    def _check_httrack_installed(self):
        """检查httrack是否已安装"""
        try:
            result = subprocess.run(['httrack', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def _download_website(self):
        """使用httrack下载网站"""
        if not self._check_httrack_installed():
            print("错误: 未安装httrack工具。请先安装httrack:")
            print("  Linux: sudo apt-get install httrack")
            print("  macOS: brew install httrack")
            print("  Windows: 下载并安装 http://www.httrack.com/page/2/")
            return False

        print(f"开始下载网站: {self.url}")
        print(f"输出目录: {self.download_dir}")
        print(f"下载深度: {self.args.depth}")

        # 构建httrack命令
        cmd = [
            'httrack', self.url,
            '--path', self.download_dir,
            '--depth', str(self.args.depth),
            '--quiet',
            '--display'
        ]

        # 如果设置了文件限制，也限制HTTrack下载的文件数量
        if self.args.limit:
            cmd.extend(['--max-files', str(self.args.limit)])
            cmd.extend(['--timeout', '60'])  # 添加超时设置
            print(f"已限制下载文件数量为: {self.args.limit}")

        # 添加自定义选项
        if self.args.httrack_options:
            cmd.extend(self.args.httrack_options.split())

        try:
            # 启动下载进程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1
            )

            # 实时显示输出
            for line in iter(process.stdout.readline, b''):
                try:
                    # 尝试多种编码解码
                    decoded_line = None
                    for encoding in ['utf-8', 'gbk', 'gb2312', 'iso-8859-1']:
                        try:
                            decoded_line = line.decode(encoding).strip()
                            break
                        except UnicodeDecodeError:
                            continue

                    # 如果所有编码都失败，使用忽略错误的方式
                    if decoded_line is None:
                        decoded_line = line.decode('utf-8', errors='replace').strip()

                    if decoded_line:
                        print(decoded_line)
                except Exception as e:
                    print(f"解码输出时出错: {str(e)}")

            # 等待进程完成
            process.wait()

            if process.returncode == 0:
                print("网站下载完成!")
                return True
            else:
                print(f"下载失败，返回代码: {process.returncode}")
                return False

        except Exception as e:
            print(f"下载时出错: {str(e)}")
            return False

    def _safe_mkdir(self, directory):
        """安全地创建目录"""
        try:
            os.makedirs(directory, exist_ok=True)
            return True
        except Exception as e:
            print(f"创建目录时出错: {str(e)}")
            return False

    def _safe_rmtree(self, directory):
        """安全地删除目录树"""
        try:
            if os.path.exists(directory):
                shutil.rmtree(directory)
            return True
        except Exception as e:
            print(f"删除目录时出错: {str(e)}")
            return False

    def _ensure_html_extension(self, url):
        """确保URL使用.html扩展名"""
        if not url:
            return url

        # 跳过外部链接、锚点和特殊协议
        if url.startswith(('http://', 'https://', 'mailto:', 'tel:', '#', 'javascript:')):
            return url

        # 替换.md为.html
        url = re.sub(r'\.md($|\?|#)', r'.html\1', url)

        # 如果URL没有扩展名且不以/结尾，添加.html
        if not re.search(r'\.[a-zA-Z0-9]+($|\?|#)', url) and not url.endswith('/'):
            url = url + '.html'

        return url

    def _fix_links_in_content(self, content):
        """修复HTML内容中的链接"""
        # 修复href属性中的链接
        content = re.sub(r'href=[\'"]([^\'"]+)[\'"]',
                        lambda m: f'href="{self._ensure_html_extension(m.group(1))}"',
                        content)

        # 修复src属性中的链接（对于图片等）
        content = re.sub(r'src=[\'"]([^\'"]+)[\'"]',
                        lambda m: f'src="{self._ensure_html_extension(m.group(1))}"',
                        content)

        # 修复绝对路径链接（添加域名目录前缀）
        content = re.sub(r'(href|src)=[\'"]/((?!{domain}).+?)[\'"]'.format(domain=re.escape(self.domain)),
                        rf'\1="/{self.domain}/\2"',
                        content)

        # 确保所有内部链接都有域名前缀
        content = re.sub(r'(href|src)=[\'"](?!http|https|ftp|mailto|tel|#|/|javascript)([^\'"]+)[\'"]',
                         rf'\1="/{self.domain}/\2"',
                         content)

        return content

    def _get_title_from_md(self, md_content):
        """从Markdown内容提取标题"""
        lines = md_content.strip().split('\n')
        for line in lines:
            # 寻找一级标题
            if line.startswith('# '):
                return line[2:].strip()
        # 如果没有找到一级标题，返回默认标题
        return "Markdown页面"

    def _convert_md_to_html(self, md_file_path, output_path):
        """将Markdown文件转换为HTML"""
        if not MARKDOWN_AVAILABLE:
            print(f"跳过Markdown转换: {md_file_path} (未安装markdown库)")
            return False

        try:
            # 读取Markdown内容
            md_content = None

            # 尝试多种编码读取文件
            for encoding in ['utf-8', 'gbk', 'gb2312', 'iso-8859-1']:
                try:
                    with open(md_file_path, 'r', encoding=encoding) as f:
                        md_content = f.read()
                    break
                except UnicodeDecodeError:
                    continue

            # 如果所有编码都失败，使用替换错误的方式
            if md_content is None:
                with open(md_file_path, 'r', encoding='utf-8', errors='replace') as f:
                    md_content = f.read()
                print(f"警告: 文件 {md_file_path} 使用了不标准的编码，可能存在乱码")

            # 提取标题
            title = self._get_title_from_md(md_content)

            # 转换Markdown为HTML
            html_content = markdown.markdown(md_content, extensions=['extra', 'tables'])

            # 创建HTML文档
            html_doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="/{self.domain}/static/index.css">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            padding: 20px;
            max-width: 900px;
            margin: 0 auto;
            color: #333;
        }}
        pre {{
            background-color: #f5f5f5;
            padding: 10px;
            overflow: auto;
            border-radius: 4px;
        }}
        code {{
            background-color: #f5f5f5;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: "SFMono-Regular", Consolas, Liberation Mono, Menlo, monospace;
        }}
        img {{ max-width: 100%; height: auto; }}
        a {{ color: #0366d6; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="book-content">
        <h1>{title}</h1>
        {html_content}
        <p style="margin-top: 30px; padding-top: 10px; border-top: 1px solid #eee;">
            <a href="/{self.domain}/index.html">返回首页</a>
        </p>
    </div>
</body>
</html>"""

            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # 写入HTML文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_doc)

            return True
        except Exception as e:
            print(f"转换Markdown文件时出错: {md_file_path}\n{str(e)}")
            return False

    def _fix_html_file(self, html_file_path, output_path):
        """修复HTML文件中的链接问题"""
        try:
            # 读取HTML内容
            html_content = None
            detected_encoding = None

            # 使用二进制模式读取文件，以便进行编码检测
            with open(html_file_path, 'rb') as f:
                raw_content = f.read()

            # 检测编码（如果内容以BOM开头，直接处理）
            if raw_content.startswith(b'\xef\xbb\xbf'):  # UTF-8 BOM
                html_content = raw_content[3:].decode('utf-8')
                detected_encoding = 'utf-8-sig'
            else:
                # 尝试多种编码
                for encoding in ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5', 'iso-8859-1']:
                    try:
                        html_content = raw_content.decode(encoding)
                        detected_encoding = encoding
                        break
                    except UnicodeDecodeError:
                        continue

            # 如果仍无法解码，使用错误替换方式
            if html_content is None:
                html_content = raw_content.decode('utf-8', errors='replace')
                detected_encoding = 'utf-8 (with replacement)'
                print(f"警告: 文件 {html_file_path} 使用了不标准的编码，使用替换字符处理")

            # 修复HTML编码声明
            html_content = re.sub(
                r'<meta[^>]*charset=["\']?([^"\'>]*)["\']?[^>]*>',
                f'<meta charset="utf-8">',
                html_content
            )

            # 如果没有编码声明，添加一个
            if 'charset=' not in html_content and '<head' in html_content:
                html_content = html_content.replace('<head>', '<head>\n    <meta charset="utf-8">')

            # 修复链接
            fixed_content = self._fix_links_in_content(html_content)

            # 如果文件没有完整的HTML结构，添加基本的HTML结构
            if "<html" not in fixed_content.lower():
                # 尝试提取标题
                title_match = re.search(r'<title>(.*?)</title>', fixed_content)
                h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', fixed_content)

                if title_match:
                    title = title_match.group(1)
                elif h1_match:
                    title = h1_match.group(1)
                else:
                    # 使用文件名作为标题
                    filename = os.path.basename(html_file_path)
                    title = os.path.splitext(filename)[0].replace('-', ' ').replace('_', ' ').title()

                # 创建完整的HTML结构
                fixed_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="/{self.domain}/static/index.css">
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="content">
            {fixed_content}
        </div>
        <p style="margin-top: 30px; padding-top: 10px; border-top: 1px solid #eee;">
            <a href="/{self.domain}/index.html">返回首页</a>
        </p>
    </div>
</body>
</html>"""

            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # 写入修复后的HTML文件，统一使用UTF-8编码
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)

            print(f"成功处理文件: {os.path.basename(html_file_path)} (原编码: {detected_encoding} -> UTF-8)")
            return True
        except Exception as e:
            print(f"修复HTML文件时出错: {html_file_path}\n{str(e)}")
            return False

    def _process_files(self):
        """处理输入目录中的文件"""
        try:
            # 清空并重建输出目录
            self._safe_rmtree(self.output_dir)
            self._safe_mkdir(self.output_dir)

            # 创建域名目录
            domain_dir = os.path.join(self.output_dir, self.domain)
            self._safe_mkdir(domain_dir)

            # 创建静态资源目录
            static_dir = os.path.join(domain_dir, 'static')
            self._safe_mkdir(static_dir)

            # 创建默认CSS文件
            self._create_default_css()

            # 扫描文件
            input_dir = self.download_dir
            file_list = []

            for root, _, files in os.walk(input_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, input_dir)
                    file_list.append((file_path, rel_path))

            self.total_count = len(file_list)
            print(f"找到 {self.total_count} 个文件")

            # 如果设置了限制，截取列表
            if self.args.limit:
                file_list = file_list[:self.args.limit]
                print(f"由于限制，将只处理前 {self.args.limit} 个文件")

            # 处理文件
            for file_path, rel_path in file_list:
                try:
                    self.processed_count += 1

                    # 计算输出路径
                    output_path = os.path.join(domain_dir, rel_path)

                    # 确保输出目录存在
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)

                    # 根据文件类型进行处理
                    if rel_path.lower().endswith('.md') and ('md-only' in self.args.file_types or 'md-html' in self.args.file_types or 'all' in self.args.file_types):
                        # 将.md改为.html
                        output_path = os.path.splitext(output_path)[0] + '.html'
                        # 转换Markdown为HTML
                        self._convert_md_to_html(file_path, output_path)
                        if self.args.verbose:
                            print(f"[{self.processed_count}/{self.total_count}] 转换MD: {rel_path}")

                    elif rel_path.lower().endswith(('.html', '.htm')) and ('html-only' in self.args.file_types or 'md-html' in self.args.file_types or 'all' in self.args.file_types):
                        # 修复HTML文件链接
                        self._fix_html_file(file_path, output_path)
                        if self.args.verbose:
                            print(f"[{self.processed_count}/{self.total_count}] 修复HTML: {rel_path}")

                    elif 'all' in self.args.file_types:
                        # 直接复制其他文件
                        shutil.copy2(file_path, output_path)
                        if self.args.verbose:
                            print(f"[{self.processed_count}/{self.total_count}] 复制: {rel_path}")

                    # 定期显示进度
                    if not self.args.verbose and self.processed_count % 50 == 0:
                        elapsed = time.time() - self.start_time
                        progress = self.processed_count / self.total_count * 100
                        print(f"进度: {progress:.1f}% ({self.processed_count}/{self.total_count}) - 用时: {elapsed:.1f}s")

                except Exception as e:
                    print(f"处理文件时出错: {rel_path}\n{str(e)}")

            return True

        except Exception as e:
            print(f"处理文件时出错: {str(e)}")
            return False

    def _create_default_css(self):
        """创建默认CSS文件"""
        css_path = os.path.join(self.output_dir, self.domain, 'static', 'index.css')
        css_content = """
/* 网站样式 */
:root {
    --main-color: #0366d6;
    --bg-color: #fff;
    --text-color: #24292e;
    --header-bg: #f6f8fa;
    --border-color: #e1e4e8;
    --hover-bg: #f6f8fa;
}

@media (prefers-color-scheme: dark) {
    :root {
        --main-color: #58a6ff;
        --bg-color: #0d1117;
        --text-color: #c9d1d9;
        --header-bg: #161b22;
        --border-color: #30363d;
        --hover-bg: #161b22;
    }
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background-color: var(--bg-color);
    margin: 0;
    padding: 0;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    background-color: var(--header-bg);
    border-bottom: 1px solid var(--border-color);
    padding: 16px 0;
    margin-bottom: 20px;
}

header .container {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

h1, h2, h3, h4 {
    margin-top: 24px;
    margin-bottom: 16px;
    font-weight: 600;
    line-height: 1.25;
}

h1 {
    font-size: 2em;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 0.3em;
}

h2 {
    font-size: 1.5em;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 0.3em;
}

a {
    color: var(--main-color);
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

.site-title {
    font-size: 1.5em;
    font-weight: bold;
    margin: 0;
}

.article-list {
    list-style: none;
    padding: 0;
}

.article-list li {
    margin-bottom: 12px;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 12px;
}

.article-list a {
    font-weight: 500;
    font-size: 1.1em;
}

.category-card {
    border: 1px solid var(--border-color);
    border-radius: 6px;
    margin-bottom: 20px;
    background-color: var(--bg-color);
}

.category-card h3 {
    margin: 0;
    padding: 12px 16px;
    background-color: var(--header-bg);
    border-bottom: 1px solid var(--border-color);
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}

.category-card ul {
    list-style: none;
    padding: 16px;
    margin: 0;
}

.category-card li {
    margin-bottom: 8px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border-color);
}

.category-card li:last-child {
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
}

/* 相应式设计 */
@media (max-width: 768px) {
    .container {
        padding: 10px;
    }

    header .container {
        flex-direction: column;
        align-items: flex-start;
    }
}
"""
        try:
            with open(css_path, 'w', encoding='utf-8') as f:
                f.write(css_content.strip())
            return True
        except Exception as e:
            print(f"创建CSS文件时出错: {str(e)}")
            return False

    def _create_index_html(self):
        """创建索引HTML页面"""
        try:
            # 准备存储文件信息
            file_info = []
            categories = {}

            # 首先扫描源目录中的文件
            print(f"扫描源目录查找文章: {self.download_dir}")
            for root, _, files in os.walk(self.download_dir):
                for file in files:
                    if file.endswith(('.html', '.htm')) and file != 'index.html':
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, self.download_dir)

                        # 计算目标位置
                        output_path = os.path.join(self.output_dir, self.domain, rel_path)

                        # 分析目录结构获取分类
                        parts = rel_path.split(os.sep)
                        if len(parts) > 1:
                            category = parts[0] if len(parts) > 1 else "其他"
                        else:
                            category = "其他"

                        # 读取文件获取标题
                        try:
                            content = None
                            # 尝试多种编码读取文件
                            for encoding in ['utf-8', 'gbk', 'gb2312', 'iso-8859-1']:
                                try:
                                    with open(file_path, 'r', encoding=encoding) as f:
                                        content = f.read()
                                    break
                                except UnicodeDecodeError:
                                    continue

                            # 如果所有编码都失败，使用替换错误的方式
                            if content is None:
                                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                                    content = f.read()

                            title_match = re.search(r'<title>(.*?)</title>', content)
                            if title_match:
                                title = title_match.group(1)
                            else:
                                h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content)
                                if h1_match:
                                    title = h1_match.group(1)
                                else:
                                    title = os.path.splitext(file)[0].replace('-', ' ').replace('_', ' ').title()
                        except Exception as e:
                            print(f"读取文件标题时出错: {rel_path} - {str(e)}")
                            title = os.path.splitext(file)[0].replace('-', ' ').replace('_', ' ').title()

                        # 构建网站内的相对路径
                        web_path = '/' + self.domain + '/' + rel_path

                        # 记录文件信息
                        info = {
                            'path': web_path,
                            'title': title,
                            'category': category
                        }
                        file_info.append(info)
                        print(f"找到文章: {rel_path} -> {title} [分类: {category}]")

                        # 按分类组织
                        if category not in categories:
                            categories[category] = []
                        categories[category].append(info)

            # 如果没有文件，添加测试文章
            if not file_info:
                print("警告: 没有找到文章，添加测试文章")
                test_category = "测试"
                test_article = {
                    'path': '/' + self.domain + '/test-article.html',
                    'title': '测试文章',
                    'category': test_category
                }
                file_info.append(test_article)
                if test_category not in categories:
                    categories[test_category] = []
                categories[test_category].append(test_article)

            # 生成HTML内容
            html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.args.title}</title>
    <link rel="stylesheet" href="/{self.domain}/static/index.css">
</head>
<body>
    <header>
        <div class="container">
            <h1 class="site-title">{self.args.title}</h1>
            <p>共 {len(file_info)} 篇文章，{len(categories)} 个分类</p>
        </div>
    </header>

    <div class="container">
        <h2>内容分类</h2>
        <div class="categories-grid">
"""

            # 添加分类卡片
            for category, files in sorted(categories.items()):
                html_content += f"""
            <div class="category-card">
                <h3>{category} ({len(files)})</h3>
                <ul>
"""

                # 添加分类下的文件
                for file in sorted(files, key=lambda x: x['title']):
                    html_content += f"""                    <li><a href="{file['path']}">{file['title']}</a></li>
"""

                html_content += """                </ul>
            </div>
"""

            # 添加页脚
            html_content += f"""
        </div>

        <footer>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
    </div>
</body>
</html>
"""

            # 写入文件
            index_path = os.path.join(self.output_dir, self.domain, 'index.html')
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            # 创建根目录索引，自动跳转到域名目录
            root_index_path = os.path.join(self.output_dir, 'index.html')
            root_index_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0;url=/{self.domain}/index.html">
    <title>正在跳转...</title>
</head>
<body>
    <p>正在跳转到 <a href="/{self.domain}/index.html">{self.args.title}</a>...</p>
</body>
</html>
"""
            with open(root_index_path, 'w', encoding='utf-8') as f:
                f.write(root_index_content)

            return True

        except Exception as e:
            print(f"创建索引页面时出错: {str(e)}")
            return False

    def _is_port_available(self, port):
        """检查端口是否可用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return True
        except:
            return False

    def _start_http_server(self):
        """启动HTTP服务器"""
        port = self.args.port

        # 检查端口是否可用
        if not self._is_port_available(port):
            # 查找可用端口
            for p in range(port+1, port+100):
                if self._is_port_available(p):
                    port = p
                    break
            else:
                print(f"无法找到可用端口，无法启动HTTP服务器")
                return False

        try:
            # 创建HTTP服务器处理器
            handler = http.server.SimpleHTTPRequestHandler

            # 切换到输出目录
            os.chdir(self.output_dir)

            # 创建服务器
            httpd = socketserver.TCPServer(("", port), handler)

            # 打印服务器信息
            url = f"http://localhost:{port}"
            index_url = f"{url}/{self.domain}/index.html"

            print(f"\nHTTP服务器已启动: {url}")
            print(f"网站主页: {index_url}")

            # 打开浏览器
            threading.Timer(1, lambda: webbrowser.open(index_url)).start()

            # 运行服务器
            print("按 Ctrl+C 停止服务器...\n")
            httpd.serve_forever()

        except KeyboardInterrupt:
            print("\n服务器已停止")
            return True
        except Exception as e:
            print(f"启动HTTP服务器时出错: {str(e)}")
            return False
