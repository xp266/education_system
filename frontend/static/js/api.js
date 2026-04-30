// API 调用
import { BACKEND_URL } from './config.js';

export async function checkLogin() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/check_login`, {
      credentials: 'include'
    });
    return await response.json();
  } catch (error) {
    console.error('检查登录失败:', error);
    return { success: false };
  }
}

export async function login(account, password) {
  try {
    const response = await fetch(`${BACKEND_URL}/api/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ account, password }),
      credentials: 'include'
    });
    return await response.json();
  } catch (error) {
    console.error('登录失败:', error);
    return { success: false, message: '登录失败，请稍后再试' };
  }
}

export async function logout() {
  try {
    await fetch(`${BACKEND_URL}/api/logout`, {
      method: 'POST',
      credentials: 'include'
    });
  } catch (error) {
    console.error('退出登录失败:', error);
  }
}

export async function sendMessage(message, conversationId, guestHistory = null) {
    try {
        const body = {
            input: message,
            conversation_id: conversationId
        };
        
        if (guestHistory && guestHistory.length > 0) {
            body.guest_history = guestHistory;
        }
        
        const response = await fetch(`${BACKEND_URL}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
            credentials: 'include'
        });
        return await response.json();
    } catch (error) {
        console.error('发送消息失败:', error);
        return { success: false };
    }
}

export async function sendMessageStream(message, conversationId, guestHistory = null, onChunk, onDone, onError) {
    try {
        const body = {
            input: message,
            conversation_id: conversationId
        };
        
        if (guestHistory !== null) {
            body.guest_history = guestHistory;
            console.log('[DEBUG] sendMessageStream - 发送 guest_history:', guestHistory);
        }
        
        const response = await fetch(`${BACKEND_URL}/api/chat/stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n\n');
            buffer = lines.pop();
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const dataStr = line.slice(6);
                    try {
                        const data = JSON.parse(dataStr);
                        // 新的API格式：传递完整的item对象
                        onChunk(data);
                        if (data.type === 'done') {
                            onDone(data.conversation_id);
                        }
                    } catch (e) {
                        console.error('解析SSE数据失败:', e);
                    }
                }
            }
        }
    } catch (error) {
        console.error('发送流式消息失败:', error);
        onError(error);
    }
}

export async function getConversations() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/conversations`, {
      credentials: 'include'
    });
    return await response.json();
  } catch (error) {
    console.error('加载对话失败:', error);
    return { success: false };
  }
}

export async function createNewConversation(title = '新对话') {
  try {
    const response = await fetch(`${BACKEND_URL}/api/conversations/new`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: title }),
      credentials: 'include'
    });
    return await response.json();
  } catch (error) {
    console.error('创建新对话失败:', error);
    return { success: false };
  }
}

export async function deleteConversation(conversationId) {
  try {
    const response = await fetch(`${BACKEND_URL}/api/conversations/${conversationId}`, {
      method: 'DELETE',
      credentials: 'include'
    });
    return await response.json();
  } catch (error) {
    console.error('删除对话失败:', error);
    return { success: false };
  }
}

export async function getConversationMessages(conversationId) {
  try {
    const response = await fetch(`${BACKEND_URL}/api/conversations/${conversationId}/messages`, {
      credentials: 'include'
    });
    return await response.json();
  } catch (error) {
    console.error('加载对话消息失败:', error);
    return { success: false };
  }
}

export async function clearConversationMessages(conversationId) {
  try {
    const response = await fetch(`${BACKEND_URL}/api/conversations/${conversationId}/messages`, {
      method: 'DELETE',
      credentials: 'include'
    });
    return await response.json();
  } catch (error) {
    console.error('清空对话消息失败:', error);
    return { success: false };
  }
}
