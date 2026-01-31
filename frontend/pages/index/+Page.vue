<script setup lang="ts">
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getStoredToken } from '../../components/api';

const router = useRouter();

onMounted(() => {
  const token = getStoredToken();
  if (token) {
    router.push('/home');
  } else {
    router.push('/login');
  }
});
</script>

<template>
  <div>正在跳转...</div>
</template>
