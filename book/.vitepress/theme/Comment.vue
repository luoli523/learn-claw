<template>
  <div class="comment-wrapper">
    <div id="waline"></div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vitepress'

const route = useRoute()
let walineInstance = null

async function initWaline() {
  if (walineInstance) {
    walineInstance.destroy()
    walineInstance = null
  }
  const { init } = await import('https://unpkg.com/@waline/client@v3/dist/waline.js')
  walineInstance = init({
    el: '#waline',
    serverURL: 'https://waline-server-amber.vercel.app',
    lang: 'zh-CN',
    pageview: true,
    comment: true,
    site: 'learn-claw',
    dark: 'html.dark',
  })
}

onMounted(() => { initWaline() })
watch(() => route.path, () => { initWaline() })
onUnmounted(() => { if (walineInstance) walineInstance.destroy() })
</script>

<style>
@import 'https://unpkg.com/@waline/client@v3/dist/waline.css';

.comment-wrapper {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid var(--vp-c-divider);
}

/* 浅色模式 */
:root {
  --waline-font-family: -apple-system, BlinkMacSystemFont, "PingFang SC",
    "Helvetica Neue", Arial, "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  --waline-font-size: 15px;
  --waline-theme-color: var(--vp-c-brand-1);
  --waline-active-color: var(--vp-c-brand-2);
  --waline-bgcolor: var(--vp-c-bg);
  --waline-bgcolor-light: var(--vp-c-bg-soft);
  --waline-border-color: var(--vp-c-divider);
  --waline-border: 1px solid var(--vp-c-divider);
  --waline-avatar-radius: 50%;
  --waline-avatar-size: 36px;
}

/* 深色模式 */
html.dark {
  --waline-color: var(--vp-c-text-1);
  --waline-bgcolor: var(--vp-c-bg);
  --waline-bgcolor-light: var(--vp-c-bg-soft);
  --waline-border-color: var(--vp-c-divider);
  --waline-border: 1px solid var(--vp-c-divider);
}

/* 输入框圆角 & 焦点色 */
.wl-editor, .wl-input {
  border-radius: 8px !important;
  font-size: 14px !important;
}

/* 提交按钮用品牌色 */
.wl-btn.primary {
  background: var(--vp-c-brand-1) !important;
  border-color: var(--vp-c-brand-1) !important;
  border-radius: 6px !important;
}
.wl-btn.primary:hover {
  background: var(--vp-c-brand-2) !important;
  border-color: var(--vp-c-brand-2) !important;
}

/* 评论卡片 */
.wl-card {
  border-radius: 8px !important;
  padding: 14px 16px !important;
}

/* 昵称颜色 */
.wl-nick {
  color: var(--vp-c-brand-1) !important;
  font-weight: 600 !important;
}
</style>
