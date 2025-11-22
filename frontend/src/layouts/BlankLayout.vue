<template>
  <div class="blank-layout">
    <router-view v-slot="{ Component, route }">
      <component v-if="Component" :is="Component" :key="route.fullPath" />
    </router-view>
  </div>
</template>

<style scoped lang="scss">
.blank-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>



















