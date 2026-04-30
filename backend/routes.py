
"""
路由模块
处理所有 API 请求
"""
from flask import request, jsonify, session, Response
from database import verify_user
import database
import json

def register_routes(app, assistant):
    """注册所有路由"""
    
    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()
        account = data.get('account', '')
        password = data.get('password', '')
        
        if not account or not password:
            return jsonify({'success': False, 'message': '账号和密码不能为空'})
        
        user_info = verify_user(account, password)
        
        if user_info:
            session['user'] = user_info
            return jsonify({
                'success': True,
                'user': {
                    'account': user_info['account'],
                    'name': user_info['name'],
                    'role': user_info['role']
                }
            })
        else:
            return jsonify({'success': False, 'message': '账号或密码错误'})
    
    @app.route('/api/logout', methods=['POST'])
    def logout():
        session.pop('user', None)
        return jsonify({'success': True})
    
    @app.route('/api/check_login', methods=['GET'])
    def check_login():
        user = session.get('user', {'role': 'visitor', 'name': '访客', 'account': ''})
        return jsonify({'success': True, 'user': user})
    
    @app.route('/api/chat', methods=['POST'])
    def chat():
        data = request.get_json()
        user_input = data.get('input', '')
        conversation_id = data.get('conversation_id', None)
        guest_history = data.get('guest_history', None)
        
        if not user_input:
            return jsonify({'success': False, 'message': '输入不能为空'})
        
        try:
            # 获取当前用户信息
            user = session.get('user', {'role': 'visitor', 'name': '访客', 'account': ''})
            result = assistant.process_query(
                user_input,
                user.get('role', 'visitor'),
                user.get('account', ''),
                user.get('name', ''),
                conversation_id,
                guest_history
            )
            
            # 处理返回结果
            return jsonify({
                'success': True,
                'response': result['response'],
                'conversation_id': result['conversation_id'],
                'is_policy': result.get('is_policy', False)
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

    @app.route('/api/chat/stream', methods=['POST'])
    def chat_stream():
        data = request.get_json()
        user_input = data.get('input', '')
        conversation_id = data.get('conversation_id', None)
        guest_history = data.get('guest_history', None)
        # print(f"[DEBUG] chat_stream - 接收到的 guest_history: {guest_history}")
        
        if not user_input:
            return jsonify({'success': False, 'message': '输入不能为空'})
        
        try:
            user = session.get('user', {'role': 'visitor', 'name': '访客', 'account': ''})
            
            def generate():
                for item in assistant.process_query_stream(
                    user_input,
                    user.get('role', 'visitor'),
                    user.get('account', ''),
                    user.get('name', ''),
                    conversation_id,
                    guest_history
                ):
                    yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"
            
            return Response(
                generate(),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no'
                }
            )
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    
    # ==================== 对话会话API ====================
    @app.route('/api/conversations', methods=['GET'])
    def get_conversations():
        user = session.get('user', None)
        if not user or user.get('role') == 'visitor':
            return jsonify({'success': False, 'message': '请先登录'})
        
        conversations = database.get_conversations(user['account'])
        return jsonify({'success': True, 'data': conversations})
    
    @app.route('/api/conversations/new', methods=['POST'])
    def new_conversation():
        user = session.get('user', None)
        if not user or user.get('role') == 'visitor':
            return jsonify({'success': False, 'message': '请先登录'})
        
        title = '新对话'
        try:
            if request.data:
                data = request.get_json()
                title = data.get('title', '新对话')
        except:
            pass
        
        conversation_id = database.create_conversation(user['account'], user['role'], title)
        return jsonify({'success': True, 'conversation_id': conversation_id})
    
    @app.route('/api/conversations/<int:conversation_id>', methods=['DELETE'])
    def delete_conversation(conversation_id):
        user = session.get('user', None)
        if not user or user.get('role') == 'visitor':
            return jsonify({'success': False, 'message': '请先登录'})
        
        success = database.delete_conversation(conversation_id)
        return jsonify({'success': success})
    
    @app.route('/api/conversations/<int:conversation_id>/messages', methods=['GET'])
    def get_conversation_messages(conversation_id):
        user = session.get('user', None)
        if not user or user.get('role') == 'visitor':
            return jsonify({'success': False, 'message': '请先登录'})
        
        messages = database.get_messages(conversation_id, limit=100)
        return jsonify({'success': True, 'data': messages})
    
    @app.route('/api/conversations/<int:conversation_id>/messages', methods=['DELETE'])
    def clear_conversation_messages(conversation_id):
        user = session.get('user', None)
        if not user or user.get('role') == 'visitor':
            return jsonify({'success': False, 'message': '请先登录'})
        
        success = database.clear_messages(conversation_id)
        return jsonify({'success': success})

