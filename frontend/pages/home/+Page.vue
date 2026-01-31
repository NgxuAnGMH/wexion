<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getCurrentUser, User, clearStoredToken } from '../../components/api';

const router = useRouter();

const user = ref<User | null>(null);
const isLoading = ref(true);
const errorMessage = ref('');

onMounted(async () => {
  try {
    const userData = await getCurrentUser();
    user.value = userData;
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '获取用户信息失败';
    // 自动跳转到登录页
    clearStoredToken();
    setTimeout(() => {
      router.push('/login');
    }, 2000);
  } finally {
    isLoading.value = false;
  }
});

function handleLogout() {
  clearStoredToken();
  router.push('/login');
}
</script>

<template>
  <div class="home-container">
    <header class="header">
      <h1>Wexion CMS</h1>
      <div class="user-info">
        <span v-if="user">欢迎, {{ user.username }}</span>
        <button @click="handleLogout" class="logout-btn">退出</button>
      </div>
    </header>

    <main class="main-content">
      <div v-if="isLoading" class="loading">
        加载中...
      </div>

      <div v-else-if="errorMessage" class="error">
        {{ errorMessage }}
        <p>即将跳转到登录页...</p>
      </div>

      <div v-else-if="user" class="welcome-card">
        <h2>欢迎使用 Wexion CMS</h2>
        <div class="user-details">
          <p><strong>用户 ID:</strong> {{ user.id }}</p>
          <p><strong>用户名:</strong> {{ user.username }}</p>
          <p v-if="user.avatar"><strong>头像:</strong> <img :src="user.avatar" alt="头像" /></p>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.home-container {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.header {
  background: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h1 {
  margin: 0;
  color: #333;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logout-btn {
  padding: 0.5rem 1rem;
  background-color: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
}

.logout-btn:hover {
  background-color: #5568d3;
}

.main-content {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.loading,
.error {
  text-align: center;
  padding: 2rem;
  font-size: 1.125rem;
}

.error {
  color: #c33;
}

.welcome-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.welcome-card h2 {
  margin-top: 0;
  color: #333;
}

.user-details {
  margin-top: 1.5rem;
}

.user-details p {
  margin-bottom: 0.75rem;
  color: #666;
}

.user-details img {
  max-width: 100px;
  border-radius: 4px;
}
</style>
