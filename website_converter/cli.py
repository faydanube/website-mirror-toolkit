#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令行接口模块

提供命令行工具入口，处理参数并调用相应功能模块
"""

import argparse
import sys
import os
import signal
from pathlib import Path
from website_converter.core import WebsiteConverter


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='网站下载、转换一体化工具')
    parser.add_argument('--url', '-u', required=False, help='要下载的网站URL，不提供则只处理本地文件')
    parser.add_argument('--output', '-o', help='输出目录，默认为：域名_html')
    parser.add_argument('--download-dir', '-d', help='下载目录，默认为：域名_httrack')
    parser.add_argument('--limit', '-l', type=int, default=None, help='限制处理的文件数量，用于测试')
    parser.add_argument('--no-download', action='store_true', help='跳过下载步骤，仅处理已下载的内容')
    parser.add_argument('--server', action='store_true', help='启动内置HTTP服务器（默认不启动）')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细输出')
    parser.add_argument('--file-types', choices=['all', 'md-only', 'html-only', 'md-html'], default='md-html',
                      help='要处理的文件类型 (all=所有文件, md-only=仅Markdown, html-only=仅HTML, md-html=仅Markdown和HTML)')
    parser.add_argument('--port', '-p', type=int, default=8080, help='HTTP服务器端口')
    parser.add_argument('--depth', type=int, default=5, help='HTTrack下载深度，默认5级')
    parser.add_argument('--httrack-options', default='', help='HTTrack附加选项')
    parser.add_argument('--title', default='网站离线镜像', help='网站标题')
    parser.add_argument('--timeout', '-t', type=int, default=3600, help='总执行时间限制，单位为秒 (default: 3600)')
    return parser.parse_args()


def main():
    """主函数，程序入口点"""
    try:
        args = parse_args()
        # 转换文件类型选项
        if args.file_types == 'all':
            args.file_types = ['all']
        elif args.file_types == 'md-only':
            args.file_types = ['md']
        elif args.file_types == 'html-only':
            args.file_types = ['html']
        elif args.file_types == 'md-html':
            args.file_types = ['md', 'html']

        # 设置超时处理
        if args.timeout > 0:
            def timeout_handler(signum, frame):
                print(f"\n超时达到 {args.timeout} 秒，程序强制停止")
                sys.exit(1)

            # 设置超时信号处理
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(args.timeout)
            print(f"已设置最大执行时间为 {args.timeout} 秒")

        converter = WebsiteConverter(args)
        converter.run()

        # 取消超时
        if args.timeout > 0:
            signal.alarm(0)

        return 0
    except KeyboardInterrupt:
        print("\n操作被用户取消")
        return 1
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
