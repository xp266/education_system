

"""
Frontend 前端服务器
端口：5000
负责渲染页面和代理 API 请求到后端
"""
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, Response, stream_with_context
import requests

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# 配置
FRONTEND_HOST = os.getenv('FRONTEND_HOST', '0.0.0.0')
FRONTEND_PORT = int(os.getenv('FRONTEND_PORT', 5000))
BACKEND_INTERNAL_URL = os.getenv('BACKEND_INTERNAL_URL', 'http://127.0.0.1:5001')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy_to_backend(path):
    """
    代理所有 /api/* 请求到后端
    """
    # 构建后端 URL
    backend_url = f"{BACKEND_INTERNAL_URL}/api/{path}"
    
    # 准备请求头（排除不需要的头）
    headers = {}
    for key, value in request.headers:
        if key.lower() not in ['host', 'content-length']:
            headers[key] = value
    
    try:
        # 处理流式响应（特别用于 SSE）
        if request.method == 'POST' and 'stream' in path:
            resp = requests.request(
                method=request.method,
                url=backend_url,
                headers=headers,
                data=request.get_data(),
                cookies=request.cookies,
                allow_redirects=False,
                stream=True
            )
            
            # 构建流式响应
            def generate():
                for chunk in resp.iter_content(chunk_size=1024):
                    if chunk:
                        yield chunk
            
            # 准备响应头
            excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
            response_headers = [
                (k, v) for k, v in resp.headers.items()
                if k.lower() not in excluded_headers
            ]
            
            return Response(
                stream_with_context(generate()),
                status=resp.status_code,
                headers=response_headers
            )
        
        # 处理普通请求
        resp = requests.request(
            method=request.method,
            url=backend_url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False
        )
        
        # 准备响应头
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        response_headers = [
            (k, v) for k, v in resp.headers.items()
            if k.lower() not in excluded_headers
        ]
        
        return Response(
            resp.content,
            status=resp.status_code,
            headers=response_headers
        )
    
    except requests.exceptions.RequestException as e:
        return Response(
            f'代理请求失败: {str(e)}',
            status=502
        )

if __name__ == '__main__':
    app.run(debug=True, host=FRONTEND_HOST, port=FRONTEND_PORT)
