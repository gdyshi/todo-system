#!/usr/bin/env python3
"""
支持 CORS 的前端 HTTP 服务器
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json

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

if __name__ == '__main__':
    import sys

    PORT = 8080
    server_address = ('', PORT)

    httpd = HTTPServer(server_address, CORSRequestHandler)

    print(f"前端服务器已启动: http://localhost:{PORT}")
    print(f"支持 CORS，允许跨端口访问")
    print("按 Ctrl+C 停止服务器...")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n服务器已停止")
        httpd.server_close()
