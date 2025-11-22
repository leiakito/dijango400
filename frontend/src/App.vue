<template>
  <router-view v-slot="{ Component, route }">
    <component v-if="Component" :is="Component" :key="route.fullPath" />
  </router-view>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

// 初始化主题
onMounted(() => {
  appStore.updateTheme()
})
</script>

<style>
/* 全局样式已在 main.css 中定义 */
</style>
