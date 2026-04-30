
/**
 * 主应用文件
 * 负责初始化和事件绑定
 */
import {
    getCurrentUser,
    setCurrentUser,
    getCurrentConversationId,
    loadGuestHistory,
    getGuestHistory
} from './state.js';
import { checkLogin } from './api.js';
import {
    updateUserDisplay,
    showLoginModal,
    hideLoginModal,
    clearChatMessages,
    addMessage,
    scrollToBottom,
    toggleSidebar,
    showSuccessModal,
    hideSuccessModal,
    showConfirmModal,
    hideConfirmModal,
    confirmCallback,
    showPolicyDetail,
    hidePolicyDetail
} from './ui.js';
import {
    setHandlerRefs,
    handleLogin,
    handleLogout,
    handleClearChat,
    handleNewConversation,
    handleSendMessage,
    loadConversationsInternal
} from './handlers.js';

// DOM 元素引用
let chatMessages, chatInput, sendBtn, clearBtn, loginBtn, logoutBtn, userDisplay;
let loginModal, closeModalBtn, doLoginBtn, loginError, newChatBtn, conversationList;
let sidebarToggle, sidebar;
let successModal, successOkBtn, confirmModal, confirmCancelBtn, confirmOkBtn;
let policyDetailModal, policyDetailClose;

// 初始化应用
export async function init() {
    console.log('初始化应用...');
    
    getDOMElements();
    
    // 暴露全局函数
    window.showPolicyDetail = showPolicyDetail;
    window.hidePolicyDetail = hidePolicyDetail;
    
    setHandlerRefs({
        chatMessages,
        chatInput,
        loginError,
        conversationList,
        successModal,
        confirmModal
    });
    
    chatInput.value = '';
    
    loadGuestHistory();
    
    const data = await checkLogin();
    if (data.success) {
        setCurrentUser(data.user);
        updateUserDisplay(loginBtn, logoutBtn, userDisplay, newChatBtn, conversationList);
        const currentUser = getCurrentUser();
        if (currentUser && currentUser.role !== 'visitor') {
            await loadConversationsInternal();
        } else {
            renderGuestHistory();
        }
    }
    
    bindEvents();
}

function getDOMElements() {
    chatMessages = document.getElementById('chat-messages');
    chatInput = document.getElementById('chat-input');
    sendBtn = document.getElementById('send-btn');
    clearBtn = document.getElementById('clear-btn');
    loginBtn = document.getElementById('login-btn');
    logoutBtn = document.getElementById('logout-btn');
    userDisplay = document.getElementById('user-display');
    loginModal = document.getElementById('login-modal');
    closeModalBtn = document.getElementById('close-modal');
    doLoginBtn = document.getElementById('do-login');
    loginError = document.getElementById('login-error');
    newChatBtn = document.getElementById('new-chat-btn');
    conversationList = document.getElementById('conversation-list');
    sidebarToggle = document.getElementById('sidebar-toggle');
    sidebar = document.getElementById('sidebar');
    successModal = document.getElementById('success-modal');
    successOkBtn = document.getElementById('success-ok-btn');
    confirmModal = document.getElementById('confirm-modal');
    confirmCancelBtn = document.getElementById('confirm-cancel-btn');
    confirmOkBtn = document.getElementById('confirm-ok-btn');
    policyDetailModal = document.getElementById('policy-detail-modal');
    policyDetailClose = document.getElementById('policy-detail-close');
    
    console.log('DOM元素获取完成:', {
        successModal, successOkBtn, confirmModal, confirmCancelBtn, confirmOkBtn
    });
}

function clearAutoFill() {
    setTimeout(() => {
        if (chatInput.value) chatInput.value = '';
    }, 10);
    setTimeout(() => {
        if (chatInput.value) chatInput.value = '';
    }, 100);
}

function renderGuestHistory() {
    clearChatMessages(chatMessages);
    
    for (const msg of getGuestHistory()) {
        addMessage(chatMessages, msg.content, msg.role);
    }
    
    scrollToBottom(chatMessages);
}

function bindEvents() {
    console.log('绑定事件...');
    
    loginBtn.addEventListener('click', () => showLoginModal(loginModal));
    closeModalBtn.addEventListener('click', () => hideLoginModal(loginModal, loginError));
    loginModal.addEventListener('click', (e) => {
        if (e.target === loginModal) hideLoginModal(loginModal, loginError);
    });
    doLoginBtn.addEventListener('click', async () => {
        const success = await handleLogin(
            document.getElementById('account'),
            document.getElementById('password')
        );
        if (success) {
            hideLoginModal(loginModal, loginError);
            showSuccessModal(successModal);
            updateUserDisplay(loginBtn, logoutBtn, userDisplay, newChatBtn, conversationList);
            await loadConversationsInternal();
        }
    });
    logoutBtn.addEventListener('click', () => {
        showConfirmModal(confirmModal, '确认退出', '确定要退出登录吗？', async () => {
            await handleLogout();
            updateUserDisplay(loginBtn, logoutBtn, userDisplay, newChatBtn, conversationList);
            clearChatMessages(chatMessages);
            conversationList.innerHTML = '';
        });
    });
    sidebarToggle.addEventListener('click', () => toggleSidebar(sidebar));
    newChatBtn.addEventListener('click', async () => {
        await handleNewConversation();
        await loadConversationsInternal();
    });
    sendBtn.addEventListener('click', handleSendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSendMessage();
    });
    clearBtn.addEventListener('click', () => {
        showConfirmModal(confirmModal, '确认清空', '确定要清空当前聊天记录吗？', handleClearChat);
    });
    successOkBtn.addEventListener('click', () => hideSuccessModal(successModal));
    successModal.addEventListener('click', (e) => {
        if (e.target === successModal) hideSuccessModal(successModal);
    });
    confirmCancelBtn.addEventListener('click', () => hideConfirmModal(confirmModal));
    confirmOkBtn.addEventListener('click', () => {
        const callback = confirmCallback;
        hideConfirmModal(confirmModal);
        if (callback) {
            callback();
        }
    });
    confirmModal.addEventListener('click', (e) => {
        if (e.target === confirmModal) hideConfirmModal(confirmModal);
    });
    
    // 政策详情弹窗关闭事件
    if (policyDetailClose) {
        policyDetailClose.addEventListener('click', hidePolicyDetail);
    }
    if (policyDetailModal) {
        policyDetailModal.addEventListener('click', (e) => {
            if (e.target === policyDetailModal) hidePolicyDetail();
        });
    }
    
    console.log('事件绑定完成');
    
    chatInput.addEventListener('focus', clearAutoFill);
    document.addEventListener('DOMContentLoaded', clearAutoFill);
    window.addEventListener('load', clearAutoFill);
}

document.addEventListener('DOMContentLoaded', init);

