
/**
 * 响应显示模块
 * 专门用于在控制台显示AI响应信息
 */

class ResponseDisplay {
    constructor() {
        this.conversationHistory = [];
    }

    /**
     * 显示AI意图分析结果
     * @param {string} intent - AI分析的意图
     */
    displayIntent(intent) {
        console.log('%c[AI意图分析]', 'color: #4CAF50; font-weight: bold;', intent);
    }

    /**
     * 显示Token消耗信息
     * @param {number} currentTokens - 当前请求消耗的Token
     * @param {number} totalTokens - 总消耗Token
     */
    displayTokenUsage(currentTokens, totalTokens) {
        console.log('%c[Token消耗]', 'color: #2196F3; font-weight: bold;', 
                   `当前: ${currentTokens}, 总计: ${totalTokens}`);
    }

    /**
     * 显示数据库查询类型
     * @param {string} queryType - 数据库查询类型
     */
    displayDatabaseQuery(queryType) {
        console.log('%c[数据库查询]', 'color: #FF9800; font-weight: bold;', queryType);
    }

    /**
     * 显示政策查询方法
     * @param {string} method - 政策查询方法/标题
     * @param {number} page - 页码
     */
    displayPolicyQuery(method, page) {
        let message = method;
        if (page) {
            message += ` (页码: ${page})`;
        }
        console.log('%c[政策查询]', 'color: #9C27B0; font-weight: bold;', message);
    }

    /**
     * 记录完整对话
     * @param {string} userInput - 用户输入
     * @param {string} aiResponse - AI响应
     * @param {object} metadata - 元数据
     */
    recordConversation(userInput, aiResponse, metadata = {}) {
        const record = {
            timestamp: new Date().toISOString(),
            userInput,
            aiResponse,
            ...metadata
        };
        this.conversationHistory.push(record);
    }

    /**
     * 获取对话历史
     */
    getHistory() {
        return this.conversationHistory;
    }

    /**
     * 清空历史
     */
    clearHistory() {
        this.conversationHistory = [];
    }
}

// 创建全局实例
const responseDisplay = new ResponseDisplay();

export default responseDisplay;

