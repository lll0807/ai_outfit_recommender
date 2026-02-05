<template>
  <div class="chat-page">
    <!-- 顶部导航 -->
    <div class="header">
      <button @click="goBack" class="back-btn">← 返回</button>
      <h1>AI 穿衣助手</h1>
      <button @click="clearHistory" class="clear-btn">清空对话</button>
    </div>

    <!-- 消息列表 -->
    <div class="message-list" ref="messageListRef">
      <div
        v-for="(msg, index) in messages"
        :key="index"
        :class="['message', msg.role]"
      >
        <div class="message-avatar">
          <img
            :src="msg.role === 'user' ? userAvatar : botAvatar"
            class="avatar-img"
            alt="avatar"
          />
        </div>
        <div class="message-content">
          <div class="message-text" v-html="renderContent(msg.content)"></div>
          <div v-if="msg.isStreaming" class="streaming-indicator"></div>
        </div>
      </div>
    </div>

    <!-- 输入框 -->
    <div class="input-area">
      <form @submit.prevent="sendMessage" class="input-form">
        <textarea
          v-model="currentInput"
          class="chat-input"
          placeholder="继续对话..."
          rows="1"
          @keydown="handleKeyDown"
        />
        <button
          type="submit"
          class="send-btn"
          :disabled="!currentInput.trim() || isLoading"
        >
          发送
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const messages = ref([])
const currentInput = ref('')
const isLoading = ref(false)
const messageListRef = ref(null)

// 头像配置
const userAvatar = '/assets/user.jpg'
const botAvatar = '/assets/bot.png'

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}

// 渲染内容（支持换行）
const renderContent = (content) => {
  if (typeof content !== 'string') {
    return String(content || '')
  }
  return content.replace(/\n/g, '<br>')
}

// 返回首页
const goBack = () => {
  router.push('/')
}

// 清空历史记录
const clearHistory = () => {
  if (confirm('确定要清空所有对话历史吗？')) {
    messages.value = []
    localStorage.removeItem('chatHistory')
    console.log('对话历史已清空')
  }
}

// 发送消息并获取流式响应
const sendMessage = async (message = null) => {
  const text = message || currentInput.value.trim()
  if (!text || isLoading.value) return

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: text
  })

  // 清空输入框
  currentInput.value = ''
  isLoading.value = true

  // 添加助手消息（初始显示"正在思考..."）
  const assistantIndex = messages.value.length
  messages.value.push({
    role: 'assistant',
    content: '正在思考...',
    isStreaming: true
  })

  await scrollToBottom()

  try {
    // 创建 SSE 连接
    const eventSource = new EventSource(
      `http://localhost:8000/chat/stream?message=${encodeURIComponent(text)}`
    )

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data)

      if (data.type === 'chunk') {
        // 如果是第一个 chunk，清空"正在思考..."
        if (messages.value[assistantIndex].content === '正在思考...') {
          messages.value[assistantIndex].content = data.content
        } else {
          messages.value[assistantIndex].content += data.content
        }
        scrollToBottom()
      } else if (data.type === 'done') {
        // 完成流式输出
        messages.value[assistantIndex].isStreaming = false
        eventSource.close()
        isLoading.value = false
      } else if (data.type === 'error') {
        // 处理错误
        messages.value[assistantIndex].content = `错误: ${data.message}`
        messages.value[assistantIndex].isStreaming = false
        eventSource.close()
        isLoading.value = false
      }
    }

    eventSource.onerror = (error) => {
      console.error('SSE Error:', error)
      messages.value[assistantIndex].content = '连接出错，请重试'
      messages.value[assistantIndex].isStreaming = false
      eventSource.close()
      isLoading.value = false
    }

  } catch (error) {
    console.error('Error:', error)
    messages.value[assistantIndex].content = `错误: ${error.message}`
    messages.value[assistantIndex].isStreaming = false
    isLoading.value = false
  }
}

// 处理键盘事件
const handleKeyDown = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

// 初始化时从 localStorage 读取历史记录
onMounted(() => {
  try {
    const savedMessages = localStorage.getItem('chatHistory')
    if (savedMessages) {
      messages.value = JSON.parse(savedMessages)
    }
  } catch (error) {
    console.error('读取历史记录失败:', error)
    messages.value = []
  }

  // 处理初始消息（从首页跳转过来）
  if (route.query.message) {
    sendMessage(route.query.message)
  }
})

// 监听 messages 变化，自动保存到 localStorage
watch(messages, (newVal) => {
  try {
    localStorage.setItem('chatHistory', JSON.stringify(newVal))
  } catch (error) {
    console.error('保存历史记录失败:', error)
  }
}, { deep: true })
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
}

.header {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  background: white;
  border-bottom: 1px solid #eee;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.back-btn {
  background: none;
  border: none;
  font-size: 16px;
  color: #666;
  cursor: pointer;
  padding: 5px 10px;
  margin-right: 10px;
  transition: color 0.3s;
}

.back-btn:hover {
  color: #667eea;
}

.header h1 {
  font-size: 18px;
  color: #333;
  margin: 0;
  flex: 1;
}

.clear-btn {
  background: #ff6b6b;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  margin-left: 10px;
}

.clear-btn:hover {
  background: #ff5252;
  transform: translateY(-1px);
}

.clear-btn:active {
  transform: translateY(0);
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message {
  display: flex;
  gap: 12px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
  background: #f0f0f0;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.message.user .message-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.message.assistant .message-avatar {
    background: #f0f0f0;
  //background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.message-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
}

.message.user .message-content {
  align-items: flex-end;
}

.message-text {
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  word-wrap: break-word;
  font-size: 15px;
}

.message.user .message-text {
  background: #95ec69;              /* 微信绿 */
  color: #000;
 border-bottom-right-radius: 4px;
}
.message.assistant .message-text {
  background: #ffffff;
  color: #000;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.message.assistant .message-text {
  background: white;
  color: #333;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.streaming-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 12px;
}

.streaming-indicator::after,
.streaming-indicator::before {
  content: '';
  width: 6px;
  height: 6px;
  background: #999;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.streaming-indicator::before {
  animation-delay: -0.32s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.input-area {
  border-top: 1px solid #eee;
  padding: 20px;
  background: white;
}

.input-form {
  display: flex;
  gap: 10px;
}

.chat-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 25px;
  font-size: 15px;
  font-family: inherit;
  resize: none;
  min-height: 46px;
  max-height: 120px;
  overflow-y: auto;
  transition: all 0.3s;
}

.chat-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.send-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s, opacity 0.3s;
  white-space: nowrap;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
}

.send-btn:active:not(:disabled) {
  transform: translateY(0);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
