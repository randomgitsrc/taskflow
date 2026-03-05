<template>
  <div class="task-detail">
    <div class="header">
      <n-button @click="goBack" style="margin-bottom: 16px;">
        ← 返回
      </n-button>
    </div>

    <div v-if="loading" style="text-align: center; padding: 40px;">
      <n-spin size="medium" />
    </div>

    <template v-else-if="task">
      <n-card title="任务详情">
        <n-space vertical :size="16">
          <n-space align="center">
            <span class="label">ID:</span>
            <span>{{ task.id }}</span>
          </n-space>
          
          <n-space align="center">
            <span class="label">标题:</span>
            <span class="value">{{ task.title }}</span>
          </n-space>

          <n-space align="center">
            <span class="label">优先级:</span>
            <n-select
              v-model:value="task.priority"
              :options="priorityOptions"
              style="width: 120px"
              @update:value="handlePriorityChange"
            />
          </n-space>
          
          <n-space align="center">
            <span class="label">状态:</span>
            <n-tag :type="statusColors[task.status] || 'default'">
              {{ statusLabels[task.status] || task.status }}
            </n-tag>
            <n-tooltip :disabled="!task.is_blocked">
              <template #trigger>
                <n-dropdown :options="statusOptions" @select="handleStatusChange" :disabled="task.is_blocked">
                  <n-button size="small" :disabled="task.is_blocked">更改状态</n-button>
                </n-dropdown>
              </template>
              <span v-if="task.is_blocked">等待父任务完成，无法更改状态</span>
            </n-tooltip>
          </n-space>

          <!-- Progress Section -->
          <n-space align="center">
            <span class="label">进度:</span>
            <n-progress
              type="line"
              :percentage="task.progress"
              :indicator-placement="'inside'"
              style="width: 200px"
            />
            <n-button size="small" @click="showProgressModal = true">更新进度</n-button>
          </n-space>
          
          <n-space align="center">
            <span class="label">负责人:</span>
            <span>{{ task.owner || '-' }}</span>
          </n-space>
          
          <n-space align="center">
            <span class="label">描述:</span>
            <span>{{ task.description || '-' }}</span>
          </n-space>

          <!-- Tags Section -->
          <n-space align="center">
            <span class="label">标签:</span>
            <n-space>
              <n-tag
                v-for="tag in taskTags"
                :key="tag.id"
                :color="{ color: tag.color, textColor: '#fff' }"
                closable
                @close="handleRemoveTag(tag.id)"
              >
                {{ tag.name }}
              </n-tag>
              <n-button size="small" @click="showTagModal = true">添加标签</n-button>
            </n-space>
          </n-space>

          <!-- Phase 4: Parent-Child Section -->
          <n-space align="center">
            <span class="label">父任务:</span>
            <template v-if="task.parent_id">
              <n-tag type="info" closable @close="handleRemoveParent">
                {{ task.parent_title || `任务 #${task.parent_id}` }}
                <n-tag v-if="task.parent_status" :type="getStatusType(task.parent_status)" size="small" style="margin-left: 4px;">
                  {{ getStatusText(task.parent_status) }}
                </n-tag>
              </n-tag>
            </template>
            <template v-else>
              <span style="color: #999;">无</span>
            </template>
          </n-space>

          <!-- Phase 4: Blocking status -->
          <n-space v-if="task.is_blocked" align="center">
            <n-tag type="warning">等待父任务完成</n-tag>
          </n-space>

          <n-space align="center">
            <span class="label">创建时间:</span>
            <span>{{ formatDate(task.created_at) }}</span>
          </n-space>
          
          <n-space align="center">
            <span class="label">更新时间:</span>
            <span>{{ formatDate(task.updated_at) }}</span>
          </n-space>
          
          <n-space align="center" v-if="task.started_at">
            <span class="label">开始时间:</span>
            <span>{{ formatDate(task.started_at) }}</span>
          </n-space>
          
          <n-space align="center" v-if="task.completed_at">
            <span class="label">完成时间:</span>
            <span>{{ formatDate(task.completed_at) }}</span>
          </n-space>
        </n-space>
      </n-card>

      <!-- Logs Section -->
      <n-card title="任务日志" style="margin-top: 16px;">
        <template #header-extra>
          <n-button size="small" @click="showLogModal = true">添加日志</n-button>
        </template>

        <n-space vertical :size="12">
          <n-empty v-if="logs.length === 0" description="暂无日志" />
          <n-timeline v-else>
            <n-timeline-item
              v-for="log in logs"
              :key="log.id"
              :title="log.message"
              :time="formatDate(log.created_at)"
            />
          </n-timeline>
        </n-space>
      </n-card>

      <!-- Comments Section -->
      <n-card title="评论" style="margin-top: 16px;">
        <template #header-extra>
          <n-button size="small" @click="showCommentModal = true">添加评论</n-button>
        </template>

        <n-space vertical :size="12">
          <n-empty v-if="comments.length === 0" description="暂无评论" />
          <n-card v-else v-for="comment in comments" :key="comment.id" size="small">
            <n-space vertical :size="4">
              <n-space align="center">
                <n-tag type="info" size="small">{{ comment.author }}</n-tag>
                <span style="color: #999; font-size: 12px;">{{ formatDate(comment.created_at) }}</span>
                <n-button text type="error" size="tiny" @click="handleDeleteComment(comment.id)">删除</n-button>
              </n-space>
              <div>{{ comment.content }}</div>
            </n-space>
          </n-card>
        </n-space>
      </n-card>

      <!-- Add Comment Modal -->
      <n-modal v-model:show="showCommentModal" preset="card" title="添加评论" style="width: 400px;">
        <n-form>
          <n-form-item label="你的名字">
            <n-input v-model:value="newComment.author" placeholder="输入你的名字" />
          </n-form-item>
          <n-form-item label="评论内容">
            <n-input
              v-model:value="newComment.content"
              type="textarea"
              placeholder="输入评论内容"
              :rows="3"
            />
          </n-form-item>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="showCommentModal = false">取消</n-button>
            <n-button type="primary" @click="handleAddComment" :loading="addingComment">添加</n-button>
          </n-space>
        </template>
      </n-modal>

      <!-- Add Log Modal -->
      <n-modal v-model:show="showLogModal" preset="card" title="添加日志" style="width: 400px;">
        <n-form>
          <n-form-item label="日志内容">
            <n-input
              v-model:value="logMessage"
              type="textarea"
              placeholder="输入日志内容"
              :rows="3"
            />
          </n-form-item>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="showLogModal = false">取消</n-button>
            <n-button type="primary" @click="handleAddLog" :loading="addingLog">添加</n-button>
          </n-space>
        </template>
      </n-modal>

      <!-- Tag Modal -->
      <n-modal v-model:show="showTagModal" preset="card" title="管理标签" style="width: 400px;">
        <n-space vertical>
          <n-space align="center">
            <n-button @click="showCreateTag = !showCreateTag">
              {{ showCreateTag ? '选择已有标签' : '创建新标签' }}
            </n-button>
          </n-space>
          
          <template v-if="showCreateTag">
            <n-form>
              <n-form-item label="标签名称">
                <n-input v-model:value="newTag.name" placeholder="输入标签名称" />
              </n-form-item>
              <n-form-item label="标签颜色">
                <n-color-picker v-model:value="newTag.color" :show-alpha="false" />
              </n-form-item>
              <n-button type="primary" @click="handleCreateTag" :loading="creatingTag">创建并添加</n-button>
            </n-form>
          </template>
          <template v-else>
            <n-checkbox-group v-model:value="selectedTags">
              <n-space vertical>
                <n-checkbox v-for="tag in availableTags" :key="tag.id" :value="tag.id" :label="tag.name" />
              </n-space>
            </n-checkbox-group>
            <n-button type="primary" @click="handleAddTags" :loading="addingTag" style="margin-top: 12px;">添加选中标签</n-button>
          </template>
        </n-space>
      </n-modal>

      <!-- Progress Update Modal -->
      <n-modal v-model:show="showProgressModal" preset="card" title="更新进度" style="width: 400px;">
        <n-form>
          <n-form-item label="进度 (0-100%)">
            <n-slider v-model:value="newProgress" :step="5" :marks="{ 0: '0%', 50: '50%', 100: '100%' }" />
            <div style="text-align: center; margin-top: 8px;">{{ newProgress }}%</div>
          </n-form-item>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="showProgressModal = false">取消</n-button>
            <n-button type="primary" @click="handleUpdateProgress" :loading="updatingProgress">更新</n-button>
          </n-space>
        </template>
      </n-modal>
    </template>

    <n-empty v-else description="任务不存在" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NButton, NCard, NSpace, NTag, NTimeline, NTimelineItem,
  NEmpty, NModal, NForm, NFormItem, NInput, NDropdown, useMessage,
  NSelect, NColorPicker, NCheckbox, NCheckboxGroup, NProgress, NSlider, NTooltip
} from 'naive-ui'
import { taskApi, tagApi, Task, TaskLog, Tag, Comment } from '../api/tasks'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const task = ref<Task | null>(null)
const logs = ref<TaskLog[]>([])
const tags = ref<Tag[]>([])
const taskTags = ref<Tag[]>([])
const allTasks = ref<Task[]>([])
const comments = ref<Comment[]>([])
const loading = ref(false)

// Modals
const showLogModal = ref(false)
const showTagModal = ref(false)
const showCreateTag = ref(false)
const showProgressModal = ref(false)
const showCommentModal = ref(false)

// Form states
const logMessage = ref('')
const addingLog = ref(false)
const newTag = ref({ name: '', color: '#3b82f6' })
const creatingTag = ref(false)
const selectedTags = ref<number[]>([])
const addingTag = ref(false)
const newProgress = ref(0)
const updatingProgress = ref(false)
const newComment = ref({ author: '', content: '' })
const addingComment = ref(false)

const goBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push({ name: 'tasks' })
  }
}

const taskId = computed(() => Number(route.params.id))

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

const priorityOptions = [
  { label: '高', value: 'high' },
  { label: '中', value: 'medium' },
  { label: '低', value: 'low' },
]

const statusOptions = Object.entries(statusLabels).map(([value, label]) => ({
  label,
  key: value,
}))

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getStatusType = (status: string) => {
  const map: Record<string, 'default' | 'info' | 'success' | 'warning' | 'error'> = {
    pending: 'default',
    in_progress: 'info',
    completed: 'success'
  }
  return map[status] || 'default'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待处理',
    in_progress: '进行中',
    completed: '已完成'
  }
  return map[status] || status
}

const loadTask = async () => {
  loading.value = true
  try {
    task.value = await taskApi.getTask(taskId.value)
    newProgress.value = task.value.progress
    logs.value = await taskApi.getLogs(taskId.value)
    taskTags.value = await tagApi.getTaskTags(taskId.value)
    comments.value = await taskApi.getComments(taskId.value)
    allTasks.value = await taskApi.getTasks()
  } catch (e) {
    message.error('加载任务失败')
  } finally {
    loading.value = false
  }
}

const loadTags = async () => {
  try {
    tags.value = await tagApi.getTags()
  } catch (e) {
    console.error('加载标签失败', e)
  }
}

const availableTags = computed(() => 
  tags.value.filter(t => !taskTags.value.some(tt => tt.id === t.id))
)

const handleStatusChange = async (status: string) => {
  try {
    await taskApi.updateStatus(taskId.value, status)
    message.success('状态已更新')
    await loadTask()
  } catch (e) {
    message.error('状态更新失败')
  }
}

const handlePriorityChange = async (priority: string) => {
  try {
    await taskApi.updateTask(taskId.value, { priority })
    message.success('优先级已更新')
  } catch (e) {
    message.error('优先级更新失败')
  }
}

const handleAddLog = async () => {
  if (!logMessage.value.trim()) {
    message.error('请输入日志内容')
    return
  }
  addingLog.value = true
  try {
    await taskApi.addLog(taskId.value, logMessage.value)
    message.success('日志已添加')
    showLogModal.value = false
    logMessage.value = ''
    await loadTask()
  } catch (e) {
    message.error('添加日志失败')
  } finally {
    addingLog.value = false
  }
}

const handleCreateTag = async () => {
  if (!newTag.value.name.trim()) {
    message.error('请输入标签名称')
    return
  }
  creatingTag.value = true
  try {
    const tag = await tagApi.createTag({ name: newTag.value.name, color: newTag.value.color })
    await tagApi.addTagToTask(taskId.value, tag.id)
    message.success('标签已创建并添加')
    showCreateTag.value = false
    newTag.value = { name: '', color: '#3b82f6' }
    await loadTask()
    await loadTags()
  } catch (e) {
    message.error('创建标签失败')
  } finally {
    creatingTag.value = false
  }
}

const handleAddTags = async () => {
  if (selectedTags.value.length === 0) {
    message.error('请选择标签')
    return
  }
  addingTag.value = true
  try {
    for (const tagId of selectedTags.value) {
      await tagApi.addTagToTask(taskId.value, tagId)
    }
    message.success('标签已添加')
    showTagModal.value = false
    selectedTags.value = []
    await loadTask()
  } catch (e) {
    message.error('添加标签失败')
  } finally {
    addingTag.value = false
  }
}

const handleRemoveTag = async (tagId: number) => {
  try {
    await tagApi.removeTagFromTask(taskId.value, tagId)
    message.success('标签已移除')
    await loadTask()
  } catch (e) {
    message.error('移除标签失败')
  }
}

// Phase 4: Remove parent task
const handleRemoveParent = async () => {
  try {
    await taskApi.updateTask(taskId.value, { parent_id: null })
    message.success('父任务已移除')
    await loadTask()
  } catch (e) {
    message.error('移除父任务失败')
  }
}

const handleUpdateProgress = async () => {
  updatingProgress.value = true
  try {
    await taskApi.updateProgress(taskId.value, newProgress.value)
    message.success('进度已更新')
    showProgressModal.value = false
    await loadTask()
  } catch (e) {
    message.error('更新进度失败')
  } finally {
    updatingProgress.value = false
  }
}

const handleAddComment = async () => {
  if (!newComment.value.author.trim() || !newComment.value.content.trim()) {
    message.error('请填写名字和评论内容')
    return
  }
  addingComment.value = true
  try {
    await taskApi.addComment(taskId.value, newComment.value.author, newComment.value.content)
    message.success('评论已添加')
    showCommentModal.value = false
    newComment.value = { author: '', content: '' }
    await loadTask()
  } catch (e) {
    message.error('添加评论失败')
  } finally {
    addingComment.value = false
  }
}

const handleDeleteComment = async (commentId: number) => {
  try {
    await taskApi.deleteComment(commentId)
    message.success('评论已删除')
    await loadTask()
  } catch (e) {
    message.error('删除评论失败')
  }
}

onMounted(() => {
  loadTask()
  loadTags()
})
</script>

<style scoped>
.task-detail {
  max-width: 800px;
}

.header {
  margin-bottom: 8px;
}

.label {
  color: #666;
  font-weight: 500;
  min-width: 80px;
}

.value {
  font-weight: 600;
}
</style>
