// 状态管理 - 使用闭包管理状态，避免直接导出
let _currentUser = null;
let _currentConversationId = null;
let _guestHistory = [];

const GUEST_HISTORY_KEY = 'guest_chat_history';
const MAX_GUEST_HISTORY = 20;

export function getCurrentUser() {
  return _currentUser;
}

export function setCurrentUser(user) {
  _currentUser = user;
}

export function getCurrentConversationId() {
  return _currentConversationId;
}

export function setCurrentConversationId(id) {
  _currentConversationId = id;
}

export function getGuestHistory() {
  return _guestHistory;
}

// ==================== 访客历史管理
export function loadGuestHistory() {
  try {
    const history = localStorage.getItem(GUEST_HISTORY_KEY);
    if (history) {
      _guestHistory = JSON.parse(history);
    }
  } catch (error) {
    console.error('加载访客历史失败:', error);
    _guestHistory = [];
  }
}

export function saveGuestHistory() {
  try {
    localStorage.setItem(GUEST_HISTORY_KEY, JSON.stringify(_guestHistory));
  } catch (error) {
    console.error('保存访客历史失败:', error);
  }
}

export function addGuestMessage(role, content) {
  _guestHistory.push({
    role: role,
    content: content,
    timestamp: Date.now()
  });
  // 限制数量
  _guestHistory = _guestHistory.slice(-MAX_GUEST_HISTORY);
  saveGuestHistory();
}

export function clearGuestHistory() {
  _guestHistory = [];
  saveGuestHistory();
}

export function formatGuestHistoryForAI() {
  return _guestHistory.map(msg => ({
    role: msg.role,
    content: msg.content
  }));
}
