<template>
  <div class="task-tree">
    <div class="header">
      <h1>任务树</h1>
      <n-button @click="loadTree">刷新</n-button>
    </div>

    <div v-if="loading" style="text-align: center; padding: 40px;">
      <n-spin size="medium" />
    </div>

    <div v-else-if="treeData.length === 0" style="text-align: center; padding: 40px; color: #999;">
      暂无任务
    </div>

    <n-tree
      v-else
      :data="treeData"
      :default-expanded-keys="expandedKeys"
      :on-update:expanded-keys="handleExpanded"
      block-line
      selectable
      @select="handleSelect"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NTree, NTag, NSpace, NIcon } from 'naive-ui'
import { taskApi, Task } from '../api/tasks'

const router = useRouter()

const treeData = ref<any[]>([])
const loading = ref(false)
const expandedKeys = ref<number[]>([])

const statusColors: Record<string, 'default' | 'primary' | 'success' | 'warning' | 'error' | 'info'> = {
  pending: 'default',
  in_progress: 'primary',
  completed: 'success',
  paused: 'warning',
  blocked: 'error',
  waiting: 'info',
  stopped: 'default',
  cancelled: 'default',
}

const statusLabels: Record<string, string> = {
  pending: '待处理',
  in_progress: '进行中',
  completed: '已完成',
  paused: '已暂停',
  blocked: '已阻塞',
  waiting: '等待中',
  stopped: '已停止',
  cancelled: '已取消',
}

const convertToTreeData = (tasks: any[]): any[] => {
  return tasks.map(task => ({
    key: task.id,
    label: () => h(NSpace, { align: 'center', size: 'small' }, {
      default: () => [
        // Phase 4: Show blocked indicator
        task.is_blocked ? h(NTag, {
          type: 'warning',
          size: 'tiny'
        }, { default: () => '⛔ 等待父任务' }) : null,
        h('span', {
          style: task.is_blocked ? 'font-weight: 500; opacity: 0.6;' : 'font-weight: 500;'
        }, task.title),
        h(NTag, {
          type: statusColors[task.status] || 'default',
          size: 'tiny'
        }, { default: () => statusLabels[task.status] || task.status }),
        // Progress indicator
        task.progress > 0 ? h('span', {
          style: 'font-size: 11px; color: #666; background: #f5f5f5; padding: 1px 6px; border-radius: 3px;'
        }, `${task.progress}%`) : null,
      ]
    }),
    children: task.children && task.children.length > 0
      ? convertToTreeData(task.children)
      : undefined,
  }))
}

const loadTree = async () => {
  loading.value = true
  try {
    const data = await taskApi.getTaskTree()
    treeData.value = convertToTreeData(data)
    // Auto expand first level
    if (data.length > 0) {
      expandedKeys.value = data.map((t: any) => t.id)
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleExpanded = (keys: number[]) => {
  expandedKeys.value = keys
}

const handleSelect = (key: number) => {
  if (key) {
    router.push({ name: 'detail', params: { id: key } })
  }
}

onMounted(() => {
  loadTree()
})
</script>

<style scoped>
.task-tree {
  max-width: 800px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header h1 {
  font-size: 24px;
  font-weight: 600;
}
</style>
