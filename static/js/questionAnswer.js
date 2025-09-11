// 提交表单处理
document.getElementById('questionForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const form = this;
    const input = document.getElementById('questionInput');
    const messageContainer = document.querySelector('.message-container');
    
    // 1. 立即显示用户问题（优化体验）
    const userMessage = document.createElement('div');
    userMessage.className = 'message user-message';
    userMessage.innerHTML = `<p><strong>问题：</strong>${input.value}</p>`;
    messageContainer.appendChild(userMessage);
    
    // 2. 显示AI正在思考的加载状态
    const loadingMessage = document.createElement('div');
    loadingMessage.className = 'message ai-message loading';
    loadingMessage.innerHTML = '<p>AI正在思考...</p>';
    messageContainer.appendChild(loadingMessage);
    
    // 3. 清空输入框
    input.value = '';
    
    // 4. 发送AJAX请求
    try {
        const response = await fetch(form.action || window.location.href, {
            method: 'POST',
            body: new FormData(form),
            headers: {
                'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });
        
        const data = await response.json();
        
        // 5. 移除加载状态
        messageContainer.removeChild(loadingMessage);
        
        // 6. 添加AI回复
        const aiMessage = document.createElement('div');
        aiMessage.className = 'message ai-message';
        aiMessage.innerHTML = `<p><strong>回答：</strong>${data.answer}</p>`;
        messageContainer.appendChild(aiMessage);
        
    } catch (error) {
        console.error('Error:', error);
        // 7. 错误处理
        messageContainer.removeChild(loadingMessage);
        const errorMessage = document.createElement('div');
        errorMessage.className = 'message error-message';
        errorMessage.innerHTML = '<p>⚠️ 提交失败，请重试</p>';
        messageContainer.appendChild(errorMessage);
    }
    
    // 8. 滚动到最新消息
    messageContainer.scrollTop = messageContainer.scrollHeight;
});