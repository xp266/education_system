// UI 操作
import { getCurrentUser } from './state.js';

// ==================== 常量定义 ====================
const DOM_IDS = {
  ACCOUNT: 'account',
  PASSWORD: 'password',
  CONFIRM_TITLE: 'confirm-title',
  CONFIRM_MESSAGE: 'confirm-message',
  POLICY_MODAL: 'policy-detail-modal',
  POLICY_CONTENT: 'policy-detail-content'
};

// 确认弹窗回调
let confirmCallback = null;

// ==================== 工具函数 ====================
function getElementSafe(id) {
  const el = document.getElementById(id);
  if (!el) console.warn(`DOM元素 ${id} 不存在`);
  return el;
}

function safeRender(renderFn, content, fallback) {
  try {
    return renderFn(content);
  } catch (e) {
    console.error('渲染失败:', e);
    return fallback;
  }
}

// ==================== 数学公式渲染 ====================
function renderMath(text) {
  if (typeof text !== 'string' || !window.katex) return text;

  const katexOptions = { displayMode: false, throwOnError: false, strict: false };
  const blockStyle = 'overflow-x:auto;overflow-y:hidden;max-width:100%;padding:5px 0;';

  text = text.replace(/(\$\$([\s\S]*?)\$\$|\\\[([\s\S]*?)\\\])/g, (match, _, math1, math2) => {
    const math = (math1 || math2)?.trim() || '';
    return safeRender(
      () => `<div style="${blockStyle}">${katex.renderToString(math, { ...katexOptions, displayMode: true })}</div>`,
      null,
      match
    );
  });

  text = text.replace(/(\$([^\$\n]+?)\$|\\\((.*?)\\\))/g, (match, _, math1, math2) => {
    const math = (math1 || math2)?.trim() || '';
    return safeRender(() => katex.renderToString(math, katexOptions), null, match);
  });

  return text;
}

function renderMarkdownAndMath(text) {
  if (!window.marked) return text;
  const mathText = renderMath(text);
  return safeRender(() => marked.parse(mathText), null, text);
}

// ==================== 用户界面 ====================
export function updateUserDisplay(loginBtn, logoutBtn, userDisplay, newChatBtn, conversationList) {
  if (!loginBtn || !logoutBtn || !userDisplay) return;
  
  const currentUser = getCurrentUser();
  const isLegalUser = currentUser && currentUser.role !== 'visitor';

  if (isLegalUser) {
    const roleText = currentUser.role === 'student' ? '学生' : '教师';
    userDisplay.textContent = `${currentUser.name} (${roleText})`;
    loginBtn.style.display = 'none';
    logoutBtn.style.display = 'block';
    if(newChatBtn) newChatBtn.style.display = 'block';
  } else {
    userDisplay.textContent = '访客';
    loginBtn.style.display = 'block';
    logoutBtn.style.display = 'none';
    if(newChatBtn) newChatBtn.style.display = 'none';
    if(conversationList) conversationList.innerHTML = '';
  }
}

// ==================== 弹窗通用操作 ====================
const toggleModal = (modal, show) => {
  if(modal) modal.classList.toggle('show', show);
};

// 登录弹窗
export function showLoginModal(loginModal) { toggleModal(loginModal, true); }
export function hideLoginModal(loginModal, loginError) {
  toggleModal(loginModal, false);
  if(loginError) loginError.style.display = 'none';
  const account = getElementSafe(DOM_IDS.ACCOUNT);
  const password = getElementSafe(DOM_IDS.PASSWORD);
  if(account) account.value = '';
  if(password) password.value = '';
}

// 登录错误
export function showLoginError(loginError, message) {
  if (!loginError) return;
  loginError.textContent = message;
  loginError.style.display = 'block';
}

// 成功弹窗
export function showSuccessModal(successModal) { toggleModal(successModal, true); }
export function hideSuccessModal(successModal) { toggleModal(successModal, false); }

// 确认弹窗
export function showConfirmModal(confirmModal, title, message, callback) {
  if (!confirmModal) return;
  const titleEl = getElementSafe(DOM_IDS.CONFIRM_TITLE);
  const messageEl = getElementSafe(DOM_IDS.CONFIRM_MESSAGE);
  if(titleEl) titleEl.textContent = title;
  if(messageEl) messageEl.textContent = message;
  confirmCallback = callback;
  toggleModal(confirmModal, true);
}

export function hideConfirmModal(confirmModal) {
  toggleModal(confirmModal, false);
  confirmCallback = null;
}

// 政策详情弹窗
export function showPolicyDetail(content) {
  const modal = getElementSafe(DOM_IDS.POLICY_MODAL);
  const contentEl = getElementSafe(DOM_IDS.POLICY_CONTENT);
  if (!modal || !contentEl) return;

  contentEl.innerHTML = renderMarkdownAndMath(content);
  toggleModal(modal, true);
}

export function hidePolicyDetail() {
  toggleModal(getElementSafe(DOM_IDS.POLICY_MODAL), false);
}

// ==================== 聊天消息 ====================
export function clearChatMessages(chatMessages) {
  if (!chatMessages) return;
  chatMessages.innerHTML = '<div class="message ai-message"><div class="message-content markdown-body">你好！我是教育系统智能助手，有什么可以帮助你的吗？</div></div>';
}

export function scrollToBottom(container) {
  if (!container) return;
  requestAnimationFrame(() => {
    container.scrollTop = container.scrollHeight;
  });
}

export function addMessage(chatMessages, text, role, isPolicy = false) {
  if (!chatMessages) return;

  const messageDiv = document.createElement('div');
  const contentDiv = document.createElement('div');
  
  messageDiv.className = `message ${role}-message`;
  contentDiv.className = `message-content markdown-body ${isPolicy ? 'policy-content' : ''}`;
  contentDiv.innerHTML = renderMarkdownAndMath(text);

  messageDiv.appendChild(contentDiv);
  chatMessages.appendChild(messageDiv);
  scrollToBottom(chatMessages);
  
  return messageDiv;
}

export function createEmptyMessage(chatMessages, role, isPolicy = false) {
  if (!chatMessages) return { messageDiv: null, contentDiv: null };

  const messageDiv = document.createElement('div');
  const contentDiv = document.createElement('div');
  
  messageDiv.className = `message ${role}-message`;
  contentDiv.className = `message-content markdown-body ${isPolicy ? 'policy-content' : ''}`;

  messageDiv.appendChild(contentDiv);
  chatMessages.appendChild(messageDiv);
  scrollToBottom(chatMessages);

  return { messageDiv, contentDiv };
}

export function updateMessage(contentDiv, text) {
  if (!contentDiv) return;
  contentDiv.innerHTML = renderMarkdownAndMath(text);
  scrollToBottom(contentDiv.closest('.chat-messages'));
}

// ==================== 侧边栏 ====================
export function toggleSidebar(sidebar) {
  if(sidebar) sidebar.classList.toggle('collapsed');
}

export { confirmCallback };