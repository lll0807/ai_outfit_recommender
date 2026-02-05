<template>
  <div class="input-page">
    <div class="input-container">
      <h1 class="title">AI 智能穿衣推荐</h1>
      <p class="subtitle">输入您的日期和地点，获取个性化穿衣建议</p>

<!--          placeholder="例如：2月6日去福州应该穿什么？"-->
      <form @submit.prevent="handleSubmit" class="input-form">
        <textarea
          v-model="userInput"
          class="input-textarea"
          :placeholder="placeholderText"
          rows="4"
          autofocus
        />
        <button
          type="submit"
          class="send-btn"
          :disabled="!userInput.trim()"
        >
          发送
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const userInput = ref('')

const handleSubmit = () => {
  if (!userInput.value.trim()) return

  // 跳转到聊天页面，携带用户消息
  router.push({
    path: '/chat',
    query: { message: userInput.value.trim() }
  })
}
// ✅ 动态 placeholder
const placeholderText = computed(() => {
  const now = new Date()
  const month = now.getMonth() + 1
  const day = now.getDate()
  return `例如：${month}月${day}日去福州应该穿什么？`
})

</script>

<style scoped>

.input-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: linear-gradient(180deg, #f5f7fa 0%, #e9ecf1 100%);
}


.input-container {
  width: 100%;
  max-width: 500px;
  text-align: center;
  background: white;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.title {
  font-size: 32px;
  color: #333;
  margin-bottom: 10px;
  font-weight: 700;
}

.subtitle {
  color: #666;
  margin-bottom: 30px;
  font-size: 14px;
}

.input-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.input-textarea {
  width: 100%;
  padding: 15px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 16px;
  resize: none;
  font-family: inherit;
  transition: all 0.3s;
}

.input-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.send-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s, opacity 0.3s;
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
