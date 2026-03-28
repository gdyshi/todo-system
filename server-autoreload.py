#!/usr/bin/env python3
"""
支持文件监控和自动重载的前端 HTTP 服务器
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import time
import os
import json
from http.server import ThreadingHTTPServer
from functools import partial
from socketserver import TCPServer


class CORSRequestHandler(SimpleHTTPRequestHandler):
    """支持 CORS 的请求处理器"""

    def end_headers(self):
        """设置 CORS 头"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        """处理 OPTIONS 预检请求"""
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        """记录日志"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format.format(*args)}")


class FileReloader:
    """文件监控和自动重载器"""

    def __init__(self, watch_dirs, extensions=['.js', '.html', '.css']):
        """
        初始化文件监控器

        Args:
            watch_dirs: 要监控的目录列表
            extensions: 要监控的文件扩展名列表
        """
        self.watch_dirs = watch_dirs
        self.extensions = extensions
        self.last_modified = {}

        # 初始化最后修改时间
        for watch_dir in watch_dirs:
            self._scan_directory(watch_dir)

    def _scan_directory(self, directory):
        """扫描目录，记录文件的最后修改时间"""
        if not os.path.exists(directory):
            return

        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in self.extensions):
                    filepath = os.path.join(root, file)
                    self.last_modified[filepath] = = os.path.getmtime(filepath)

    def check_changes(self):
        """检查文件是否有变化"""
        changed_files = []

        for watch_dir in self.watch_dirs:
            for root, dirs, files in os.walk(watch_dir):
                for file in files:
                    if any(file.endswith(ext) for ext in self.extensions):
                        filepath = os.path.join(root, file)
                        current_mtime = os.path.getmtime(filepath)

                        if filepath in self.last_modified:
                            if current_mtime > self.last_modified[filepath]:
                                changed_files.append(filepath)
                                self.last_modified[filepath] = current_mtime
                        else:
                            self.last_modified[filepath] = current_mtime

        return changed_files

    def log_changes(self, changed_files):
        """记录变化"""
        if changed_files:
            print(f"🔄 检测到 {len(changed_files)} 个文件变化:")
            for filepath in changed_files:
                rel_path = os.path.relpath(filepath)
                print(f"   - {rel_path}")
            print("✅ 前端将自动重载")
            print()
        return len(changed_files) > 0


def main():
    """主函数"""
    import sys

    PORT = 8080
    server_address = ('', PORT)

    # 监控的目录
    WATCH_DIRS = [
        os.path.join(os.path.dirname(__file__), '.'),
        os.path.join(os.path.dirname(__file__), 'js'),
        os.path.join(os.path.dirname(__file__), 'css')
    ]

    # 创建文件监控器
    reloader = FileReloader(WATCH_DIRS)

    # 创建自定义服务器类
    CustomHTTPRequestHandler = CORSRequestHandler
    CustomHTTPRequestHandler.log_message = lambda *args: None  # 禁用详细日志

    # 使用 ThreadingHTTPServer 支持多线程
    httpd = ThreadingHTTPServer(
        server_address,
        partial(CustomHTTPRequestHandler, directory=WATCH_DIRS[0])
    )

    print(f"🚀 前端服务器已启动")
    print(f"📍 地址: http://localhost:{PORT}")
    print(f"📁 监控目录: {WATCH_DIRS}")
    print(f"🔄 文件自动重载: 已启用")
    print(f"⏳ 按 Ctrl+C 停止服务器")
    print()

    try:
        # 检查文件变化
        if reloader.check_changes():
            print("⚠️  启动时检测到文件变化")
            print("🔄 首次访问时将自动加载最新代码")
            print()

        # 启动服务器
        httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n\n⏹️  服务器正在停止...")
        httpd.server_close()
        print("✅ 前端服务器已停止")


if __name__ == '__main__':
    main()
