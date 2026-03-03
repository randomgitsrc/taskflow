<template>
  <div class="stats-page">
    <div class="header">
      <h1>任务统计</h1>
      <n-button @click="loadStats">刷新</n-button>
    </div>

    <n-spin :show="loading">
      <!-- Stats Cards -->
      <n-grid :cols="4" :x-gap="16" :y-gap="16" style="margin-bottom: 24px;">
        <n-gi>
          <n-card>
            <n-statistic label="总任务数" :value="stats.total" />
          </n-card>
        </n-gi>
        <n-gi>
          <n-card>
            <n-statistic label="进行中" :value="stats.in_progress">
              <template #prefix>
                <span style="color: #2080f0;">🟦</span>
              </template>
            </n-statistic>
          </n-card>
        </n-gi>
        <n-gi>
          <n-card>
            <n-statistic label="已完成" :value="stats.completed">
              <template #prefix>
                <span style="color: #18a058;">✅</span>
              </template>
            </n-statistic>
          </n-card>
        </n-gi>
        <n-gi>
          <n-card>
            <n-statistic label="待处理" :value="stats.pending">
              <template #prefix>
                <span style="color: #999;">⏳</span>
              </template>
            </n-statistic>
          </n-card>
        </n-gi>
      </n-grid>

      <n-grid :cols="2" :x-gap="16" :y-gap="16">
        <!-- Completion Rate -->
        <n-gi>
          <n-card title="完成率">
            <div style="text-align: center; padding: 24px;">
              <n-progress
                type="circle"
                :percentage="stats.completed_rate * 100"
                :color="progressColor"
                :rail-color="'#eee'"
                :stroke-width="12"
              >
                <div style="font-size: 24px; font-weight: bold;">
                  {{ Math.round(stats.completed_rate * 100) }}%
                </div>
              </n-progress>
            </div>
          </n-card>
        </n-gi>

        <!-- Other Stats -->
        <n-gi>
          <n-card title="其他统计">
            <n-space vertical :size="16">
              <n-space justify="space-between">
                <span>逾期任务:</span>
                <n-tag type="error">{{ stats.overdue }} 个</n-tag>
              </n-space>
              <n-space justify="space-between">
                <span>平均耗时:</span>
                <n-tag type="info">{{ stats.avg_duration_hours }} 小时</n-tag>
              </n-space>
            </n-space>
          </n-card>
        </n-gi>
      </n-grid>

      <!-- Status Distribution -->
      <n-card title="任务状态分布" style="margin-top: 16px;">
        <n-space vertical :size="12">
          <n-space justify="space-between" align="center">
            <span>待处理</span>
            <n-progress
              type="line"
              :percentage="stats.total ? (stats.pending / stats.total * 100) : 0"
              :color="'#999'"
              :show-indicator="false"
              style="width: 200px;"
            />
            <span>{{ stats.pending }}</span>
          </n-space>
          <n-space justify="space-between" align="center">
            <span>进行中</span>
            <n-progress
              type="line"
              :percentage="stats.total ? (stats.in_progress / stats.total * 100) : 0"
              :color="'#2080f0'"
              :show-indicator="false"
              style="width: 200px;"
            />
            <span>{{ stats.in_progress }}</span>
          </n-space>
          <n-space justify="space-between" align="center">
            <span>已完成</span>
            <n-progress
              type="line"
              :percentage="stats.total ? (stats.completed / stats.total * 100) : 0"
              :color="'#18a058'"
              :show-indicator="false"
              style="width: 200px;"
            />
            <span>{{ stats.completed }}</span>
          </n-space>
        </n-space>
      </n-card>
    </n-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { 
  NButton, NCard, NSpace, NStatistic, NGrid, NGi, 
  NProgress, NSpin, NTag, useMessage 
} from 'naive-ui'
import { statsApi, Stats } from '../api/tasks'

const message = useMessage()

const loading = ref(false)
const stats = ref<Stats>({
  total: 0,
  pending: 0,
  in_progress: 0,
  completed: 0,
  completed_rate: 0,
  overdue: 0,
  avg_duration_hours: 0,
})

const progressColor = computed(() => {
  const rate = stats.value.completed_rate
  if (rate >= 0.8) return '#18a058'
  if (rate >= 0.5) return '#f0a020'
  return '#d03050'
})

const loadStats = async () => {
  loading.value = true
  try {
    stats.value = await statsApi.getStats()
  } catch (e) {
    message.error('加载统计失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.stats-page {
  max-width: 1000px;
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
