<template>
  <n-config-provider>
    <n-message-provider>
      <n-layout class="app-layout">
        <!-- 顶层通栏 Header -->
        <n-layout-header class="app-header" bordered>
          <div class="header-content">
            <div class="header-left">
              <div class="logo-box">
                <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTgwIiBoZWlnaHQ9IjM2IiB2aWV3Qm94PSIwIDAgMTgwIDM2IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHg9IjIiIHk9IjgiIHdpZHRoPSIyNCIgaGVpZ2h0PSIyMCIgcng9IjQiIGZpbGw9IiNkYmVhZmUiLz48cGF0aCBkPSJNOCAxOEwxMSAyMUwxOCAxMiIgc3Ryb2tlPSIjMjJjNTUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+PHBhdGggZD0iTTMwIDE4SDMzIiBzdHJva2U9IiMxYTU2ZGIiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+PHJlY3QgeD0iMzgiIHk9IjgiIHdpZHRoPSIyNCIgaGVpZ2h0PSIyMCIgcng9IjQiIGZpbGw9IiNkYmVhZmUiLz48cmVjdCB4PSI0MiIgeT0iMTYiIHdpZHRoPSIxNiIgaGVpZ2h0PSI0IiByeD0iMiIgZmlsbD0iIzFhNTZkYiIvPjxwYXRoIGQ9Ik02NiAxOEw3MCIgc3Ryb2tlPSIjMWE1NmRiIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPjxyZWN0IHg9Ijc0IiB5PSI4IiB3aWR0aD0iMjQiIGhlaWdodD0iMjAiIHJ4PSI0IiBmaWxsPSIjZGJlYWZlIi8+PGNpcmNsZSBjeD0iODYiIGN5PSIxOCIgcj0iMyIgZmlsbD0iIzk0YTNiOCIvPjxwYXRoIGQ9Ik0xMTAgNkwxMzIgMThMMTEwIDMwIiBzdHJva2U9IiMxYTU2ZGIiIHN0cm9rZS13aWR0aD0iNCIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+PGNpcmNsZSBjeD0iMTM4IiBjeT0iMTgiIHI9IjUiIGZpbGw9IiMxYTU2ZGIiLz48L3N2Zz4=" alt="AITaskFlow" class="logo-img" />
              </div>
            </div>
            <div class="header-right">
              <n-input-group class="search-box">
                <n-input
                  v-model:value="searchQuery"
                  placeholder="搜索任务..."
                  clearable
                  style="width: 300px"
                  @keyup.enter="handleSearch"
                />
                <n-button type="primary" class="search-btn" @click="handleSearch">
                  <n-icon>
                    <search-outline />
                  </n-icon>
                </n-button>
              </n-input-group>
            </div>
          </div>
        </n-layout-header>

        <!-- 下方内容区：左侧菜单 + 右侧内容 -->
        <n-layout has-sider class="main-layout">
          <n-layout-sider
            class="app-sider"
            bordered
            collapse-mode="width"
            :collapsed-width="64"
            :width="200"
            show-trigger
            :native-scrollbar="false"
          >
            <n-menu
              class="dark-menu"
              :collapsed-width="64"
              :collapsed-icon-size="22"
              :options="menuOptions"
              :value="activeMenu"
              @update:value="handleMenuUpdate"
            />
          </n-layout-sider>
          <n-layout-content class="app-content" content-style="padding: 24px;">
            <router-view />
          </n-layout-content>
        </n-layout>
      </n-layout>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { h, ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NIcon, NLayoutHeader, NInput, NButton, NInputGroup } from 'naive-ui'
import type { MenuOption } from 'naive-ui'
import {
  ListOutline,
  GitNetworkOutline,
  DocumentTextOutline,
  StatsChartOutline,
  FolderOutline,
  SearchOutline,
} from '@vicons/ionicons5'

const router = useRouter()
const route = useRoute()

const activeMenu = computed(() => route.name as string)
const searchQuery = ref('')

const renderIcon = (icon: any) => {
  return () => h(NIcon, null, { default: () => h(icon) })
}

const menuOptions: MenuOption[] = [
  {
    label: '任务列表',
    key: 'tasks',
    icon: renderIcon(ListOutline),
  },
  {
    label: '统计',
    key: 'stats',
    icon: renderIcon(StatsChartOutline),
  },
  {
    label: '项目',
    key: 'projects',
    icon: renderIcon(FolderOutline),
  },
]

const handleMenuUpdate = (key: string) => {
  router.push({ name: key })
}

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ path: '/', query: { q: searchQuery.value } })
    searchQuery.value = ''
  }
}
</script>

<style>
/* CSS Variables */
:root {
  --primary-color: #1a56db;
  --primary-light: #dbeafe;
  --accent-color: #f97316;
  --bg-color: #f8fafc;
  --sider-bg: #1e293b;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --border-color: #e2e8f0;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
}

.app-layout {
  height: 100%;
  background: var(--bg-color);
}

/* Header Styles */
.app-header {
  height: 64px;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-box {
  background: transparent;
  padding: 4px 0;
  box-shadow: none;
  display: flex;
  align-items: center;
}

.logo-img {
  height: 32px;
  width: auto;
}

.logo {
  font-size: 24px;
  line-height: 1;
}

.logo-icon {
  font-size: 28px;
  color: var(--primary-color);
}

.brand-section {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.brand {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary-color);
  line-height: 1.2;
}

.slogan {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.2;
}

/* Search Box */
.search-box {
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.search-box .n-input {
  background: var(--bg-color);
}

.search-btn {
  background: var(--primary-color) !important;
  border-color: var(--primary-color) !important;
}

.search-btn:hover {
  background: #1e40af !important;
  border-color: #1e40af !important;
}

/* Main Layout */
.main-layout {
  background: var(--bg-color);
}

/* Sider Styles */
.app-sider {
  background: #dbeafe !important;
}

.app-sider .n-layout-sider-scroll-container {
  background: #dbeafe !important;
}

.dark-menu {
  background: transparent !important;
  --n-item-text-color: #1e293b !important;
  --n-item-icon-color: #64748b !important;
  --n-item-text-color-hover: #1a56db !important;
  --n-item-icon-color-hover: #1a56db !important;
  --n-item-text-color-active: white !important;
  --n-item-icon-color-active: white !important;
  --n-item-color-active: #1a56db !important;
  --n-item-color-active-hover: #1a56db !important;
}

.dark-menu .n-menu-item {
  margin: 4px 8px !important;
  border-radius: 8px !important;
}

.dark-menu .n-menu-item-content {
  padding: 0 16px !important;
}

.dark-menu .n-menu-item-content__icon {
  color: #64748b !important;
}

.dark-menu .n-menu-item:hover .n-menu-item-content__icon,
.dark-menu .n-menu-item:hover .n-menu-item-content-header {
  color: #1a56db !important;
}

.dark-menu .n-menu-item--selected .n-menu-item-content__icon,
.dark-menu .n-menu-item--selected .n-menu-item-content-header {
  color: white !important;
}

/* Content Area */
.app-content {
  background: var(--bg-color);
}

/* Card Styles (全局卡片样式) */
.n-card {
  border-radius: 12px !important;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
  border: none !important;
}

.n-card__content {
  padding: 20px !important;
}

/* Button Styles */
.n-button--primary-type {
  background: var(--primary-color) !important;
  border-color: var(--primary-color) !important;
}

.n-button--primary-type:hover {
  background: #1e40af !important;
  border-color: #1e40af !important;
}

/* Tag Styles - 使用 accent color */
.n-tag--type-success {
  background: #dcfce7 !important;
  color: #166534 !important;
}

.n-tag--type-warning {
  background: #ffedd5 !important;
  color: #9a3412 !important;
}

.n-tag--type-error {
  background: #fee2e2 !important;
  color: #991b1b !important;
}

.n-tag--type-info {
  background: var(--primary-light) !important;
  color: var(--primary-color) !important;
}
</style>
