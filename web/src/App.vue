<template>
  <n-config-provider>
    <n-message-provider>
      <n-layout class="app-layout" has-sider>
        <n-layout-sider
          bordered
          collapse-mode="width"
          :collapsed-width="64"
          :width="200"
          show-trigger
          :native-scrollbar="false"
          content-style="padding: 16px;"
        >
          <n-menu
            :collapsed-width="64"
            :collapsed-icon-size="22"
            :options="menuOptions"
            :value="activeMenu"
            @update:value="handleMenuUpdate"
          />
        </n-layout-sider>
        <n-layout-content content-style="padding: 24px;">
          <router-view />
        </n-layout-content>
      </n-layout>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { h, ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NIcon } from 'naive-ui'
import type { MenuOption } from 'naive-ui'
import {
  ListOutline,
  GitNetworkOutline,
  DocumentTextOutline,
  StatsChartOutline,
  FolderOutline,
} from '@vicons/ionicons5'

const router = useRouter()
const route = useRoute()

const activeMenu = computed(() => route.name as string)

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
    label: '任务树',
    key: 'tree',
    icon: renderIcon(GitNetworkOutline),
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
</script>

<style>
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
}
</style>
