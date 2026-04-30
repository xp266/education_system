
/**
 * 前端业务处理模块
 * 处理各类交互逻辑
 */
import {
    getCurrentUser,
    setCurrentUser,
    getCurrentConversationId,
    setCurrentConversationId,
    clearGuestHistory,
    addGuestMessage,
    formatGuestHistoryForAI
} from './state.js';
import {
    checkLogin,
    login,
    logout,
    getConversations,
    createNewConversation,
    deleteConversation,
    getConversationMessages,
    clearConversationMessages,
    sendMessageStream
} from './api.js';
import {
    updateUserDisplay,
    showLoginModal,
    hideLoginModal,
    showLoginError,
    clearChatMessages,
    addMessage,
    scrollToBottom,
    showSuccessModal,
    showConfirmModal,
    hideConfirmModal,
    createEmptyMessage,
    updateMessage,
    showPolicyDetail,
    hidePolicyDetail
} from './ui.js';

let chatMessages, chatInput, loginError, conversationList, successModal, confirmModal;

export function setHandlerRefs(refs) {
    chatMessages = refs.chatMessages;
    chatInput = refs.chatInput;
    loginError = refs.loginError;
    conversationList = refs.conversationList;
    successModal = refs.successModal;
    confirmModal = refs.confirmModal;
}

export async function handleLogin(accountInput, passwordInput) {
    const account = accountInput.value;
    const password = passwordInput.value;
    
    if (!account || !password) {
        showLoginError(loginError, '请输入账号和密码');
        return;
    }
    
    const data = await login(account, password);
    if (data.success) {
        setCurrentUser(data.user);
        return true;
    } else {
        showLoginError(loginError, data.message || '登录失败');
        return false;
    }
}

export async function handleLogout() {
    await logout();
    setCurrentUser(null);
    setCurrentConversationId(null);
}

export async function handleClearChat() {
    const currentUser = getCurrentUser();
    const conversationId = getCurrentConversationId();
    
    clearChatMessages(chatMessages);
    
    if (currentUser && currentUser.role === 'visitor') {
        clearGuestHistory();
    } else if (conversationId) {
        await clearConversationMessages(conversationId);
    }
}

export async function handleNewConversation() {
    const currentUser = getCurrentUser();
    if (!currentUser || currentUser.role === 'visitor') return;
    
    const data = await createNewConversation();
    if (data.success) {
        setCurrentConversationId(data.conversationId);
        clearChatMessages(chatMessages);
        return true;
    }
    return false;
}

export async function handleDeleteConversation(conversationId) {
    const data = await deleteConversation(conversationId);
    if (data.success) {
        const currentId = getCurrentConversationId();
        if (conversationId === currentId) {
            setCurrentConversationId(null);
            return true;
        }
    }
    return false;
}

export async function handleSendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    addMessage(chatMessages, message, 'user');
    chatInput.value = '';

    const currentUser = getCurrentUser();
    let guestHistoryData = null;

    if (currentUser && currentUser.role === 'visitor') {
        addGuestMessage('user', message);
        guestHistoryData = formatGuestHistoryForAI();
        guestHistoryData = guestHistoryData.slice(0, -1);
        console.log('[DEBUG] 发送访客历史:', guestHistoryData);
    }

    const { contentDiv } = createEmptyMessage(chatMessages, 'ai');
    let fullResponse = '';
    let dotInterval = null;
    let currentStatus = 'thinking';
    
    // 状态文本映射
    const statusTexts = {
        'thinking': '正在思考你的问题',
        'querying_db': '正在为您查询数据库',
        'querying_policy': '正在为您查询政策',
        'complex_analyzing': '正在识别这是一个复杂查询',
        'complex_splitting': '正在为您拆分查询问题',
        'complex_querying_db': '正在为您查询相关数据',
        'complex_querying_policy': '正在为您查询相关政策',
        'complex_generating': '正在为您生成综合回答',
        'complex_combining': '正在整合查询结果'
    };
    
    // 显示初始状态和三点动画
    function updateStatusDisplay(status) {
        currentStatus = status;
        const baseText = statusTexts[status] || statusTexts['thinking'];
        contentDiv.innerHTML = `<span class="status-text">${baseText}</span><span class="loading-dots"></span>`;
    }
    
    // 开始三点动画
    function startDotAnimation() {
        let dotCount = 0;
        dotInterval = setInterval(() => {
            const dotsSpan = contentDiv.querySelector('.loading-dots');
            if (dotsSpan) {
                dotCount = (dotCount + 1) % 4;
                dotsSpan.textContent = '.'.repeat(dotCount);
            }
        }, 400);
    }
    
    // 停止三点动画
    function stopDotAnimation() {
        if (dotInterval) {
            clearInterval(dotInterval);
            dotInterval = null;
        }
    }
    
    // 初始显示状态
    updateStatusDisplay('thinking');
    startDotAnimation();

    const currentConversationId = getCurrentConversationId();

    await sendMessageStream(
        message,
        currentConversationId,
        guestHistoryData,
        (item) => {
            if (item.type === 'status') {
                // 状态更新
                updateStatusDisplay(item.status);
            } else if (item.type === 'content') {
                // 内容更新 - 先停止动画再显示内容
                stopDotAnimation();
                fullResponse += item.data;
                updateMessage(contentDiv, fullResponse);
                if (item.isPolicy) {
                    contentDiv.classList.add('policy-content');
                }
            }
        },
        async (conversationId) => {
            stopDotAnimation();
            if (currentUser && currentUser.role === 'visitor') {
                addGuestMessage('assistant', fullResponse);
            }

            if (conversationId) {
                setCurrentConversationId(conversationId);
            }

            if (currentUser && currentUser.role !== 'visitor') {
                await loadConversationsInternal();
            }
        },
        (error) => {
            stopDotAnimation();
            console.error('流式请求错误:', error);
            if (!fullResponse) {
                updateMessage(contentDiv, '抱歉，处理失败了，请稍后再试');
            }
        }
    );
}

export async function loadConversationsInternal() {
    const currentUser = getCurrentUser();
    if (!currentUser || currentUser.role === 'visitor') return;
    
    const data = await getConversations();
    if (data.success && data.data.length > 0) {
        renderConversationsInternal(data.data);
        selectConversationInternal(data.data[0].conversation_id);
    } else {
        await handleNewConversation();
    }
}

function renderConversationsInternal(conversations) {
    conversationList.innerHTML = '';
    const currentConversationId = getCurrentConversationId();
    
    conversations.forEach(conv => {
        const item = document.createElement('div');
        item.className = 'conversation-item';
        if (conv.conversation_id === currentConversationId) {
            item.classList.add('active');
        }
        
        item.innerHTML = `
            <span class="conversation-title">${conv.title}</span>
            <button class="delete-btn" data-id="${conv.conversation_id}">×</button>
        `;
        
        item.addEventListener('click', (e) => {
            if (!e.target.classList.contains('delete-btn')) {
                selectConversationInternal(conv.conversation_id);
            }
        });
        
        item.querySelector('.delete-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            showConfirmModal(confirmModal, '确认删除', '确定要删除这个对话记录吗？', () => {
                handleDeleteConversation(conv.conversation_id).then(() => loadConversationsInternal());
            });
        });
        
        conversationList.appendChild(item);
    });
}

async function selectConversationInternal(conversationId) {
    const currentId = getCurrentConversationId();
    if (conversationId === currentId) return;
    
    setCurrentConversationId(conversationId);
    
    document.querySelectorAll('.conversation-item').forEach(item => {
        item.classList.remove('active');
        if (parseInt(item.querySelector('.delete-btn').dataset.id) === conversationId) {
            item.classList.add('active');
        }
    });
    
    await loadConversationMessagesInternal(conversationId);
}

async function loadConversationMessagesInternal(conversationId) {
    const data = await getConversationMessages(conversationId);
    if (data.success) {
        chatMessages.innerHTML = '';
        if (data.data.length === 0) {
            clearChatMessages(chatMessages);
        } else {
            data.data.forEach(msg => {
                addMessage(chatMessages, msg.content, msg.role === 'user' ? 'user' : 'ai');
            });
        }
        scrollToBottom(chatMessages);
    }
}

export { renderConversationsInternal, selectConversationInternal, loadConversationMessagesInternal };

