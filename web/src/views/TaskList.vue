<template>
  <div class="task-list">
    <div class="header">
      <h1>任务列表</h1>
      <n-button type="primary" @click="showCreateModal = true">
        新建任务
      </n-button>
    </div>

    <n-space style="margin-bottom: 16px;">
      <n-select
        v-model:value="statusFilter"
        :options="statusOptions"
        placeholder="筛选状态"
        clearable
        style="width: 150px"
        @update:value="loadTasks"
      />
      <n-select
        v-model:value="priorityFilter"
        :options="priorityOptions"
        placeholder="筛选优先级"
        clearable
        style="width: 150px"
        @update:value="loadTasks"
      />
      <n-select
        v-model:value="tagFilter"
        :options="tagOptions"
        placeholder="筛选标签"
        clearable
        style="width: 150px"
        @update:value="loadTasks"
      />
      <n-button @click="loadTasks">刷新</n-button>
    </n-space>

    <n-data-table
      :columns="columns"
      :data="tasks"
      :loading="loading"
      :row-key="(row: Task) => row.id"
      :pagination="false"
    />

    <!-- Create Modal -->
    <n-modal v-model:show="showCreateModal" preset="card" title="新建任务" style="width: 500px;">
      <n-form ref="formRef" :model="form" :rules="rules">
        <n-form-item label="标题" path="title">
          <n-input v-model:value="form.title" placeholder="输入任务标题" />
        </n-form-item>
        <n-form-item label="描述">
          <n-input v-model:value="form.description" type="textarea" placeholder="输入任务描述" />
        </n-form-item>
        <n-form-item label="父任务">
          <n-select
            v-model:value="form.parent_id"
            :options="parentTaskOptions"
            placeholder="选择父任务（可选）"
            clearable
            style="width: 100%"
          />
        </n-form-item>
        <n-form-item label="项目">
          <n-select
            v-model:value="form.project_id"
            :options="projectOptions"
            placeholder="选择项目"
            clearable
            style="width: 100%"
          />
        </n-form-item>
        <n-form-item label="优先级">
          <n-select
            v-model:value="form.priority"
            :options="priorityOptions"
            placeholder="选择优先级"
            style="width: 100%"
          />
        </n-form-item>
        <n-form-item label="负责人">
          <n-input v-model:value="form.owner" placeholder="输入负责人" />
        </n-form-item>
        <n-form-item label="标签">
          <n-select
            v-model:value="form.tag_ids"
            :options="tagOptions"
            multiple
            placeholder="选择标签"
            style="width: 100%"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showCreateModal = false">取消</n-button>
          <n-button type="primary" @click="handleCreate" :loading="creating">创建</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- Edit Modal -->
    <n-modal v-model:show="showEditModal" preset="card" title="编辑任务" style="width: 500px;">
      <n-form ref="formRef" :model="editForm">
        <n-form-item label="标题">
          <n-input v-model:value="editForm.title" />
        </n-form-item>
        <n-form-item label="描述">
          <n-input v-model:value="editForm.description" type="textarea" />
        </n-form-item>
        <n-form-item label="父任务">
          <n-select
            v-model:value="editForm.parent_id"
            :options="parentTaskOptions"
            placeholder="选择父任务（可选）"
            clearable
            style="width: 100%"
          />
        </n-form-item>
        <n-form-item label="项目">
          <n-select
            v-model:value="editForm.project_id"
            :options="projectOptions"
            placeholder="选择项目"
            clearable
            style="width: 100%"
          />
        </n-form-item>
        <n-form-item label="优先级">
          <n-select
            v-model:value="editForm.priority"
            :options="priorityOptions"
            style="width: 100%"
          />
        </n-form-item>
        <n-form-item label="负责人">
          <n-input v-model:value="editForm.owner" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showEditModal = false">取消</n-button>
          <n-button type="primary" @click="handleUpdate" :loading="updating">保存</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h, computed } from 'vue'
import { useRouter } from 'vue-router'
import { 
  NButton, NDataTable, NSpace, NModal, NForm, NFormItem, 
  NInput, NSelect, NTag, NIcon, useMessage 
} from 'naive-ui'
import { taskApi, tagApi, projectApi, Task, TaskCreate, TaskUpdate, Tag, Project } from '../api/tasks'
import {
  CreateOutline,
  TrashOutline,
  EllipsisVerticalOutline,
} from '@vicons/ionicons5'

const router = useRouter()
const message = useMessage()

const tasks = ref<Task[]>([])
const tags = ref<Tag[]>([])
const projects = ref<Project[]>([])
const loading = ref(false)
const statusFilter = ref<string | null>(null)
const priorityFilter = ref<string | null>(null)
const tagFilter = ref<number | null>(null)
const showCreateModal = ref(false)
const showEditModal = ref(false)
const creating = ref(false)
const updating = ref(false)

const form = ref<TaskCreate>({
  title: '',
  description: '',
  owner: '',
  parent_id: null,
  project_id: 1,  // Default to "未分类"
  priority: 'medium',
  tag_ids: [],
})

// Phase 4: Track current project for parent task filtering
const currentProjectId = ref<number | null>(1)

const editForm = ref<TaskUpdate>({
  title: '',
  description: '',
  owner: '',
  parent_id: null,
  project_id: null,
  priority: 'medium',
})

const editingId = ref<number | null>(null)

const rules = {
  title: { required: true, message: '请输入标题', trigger: 'blur' },
}

const statusOptions = [
  { label: '待处理', value: 'pending' },
  { label: '进行中', value: 'in_progress' },
  { label: '已完成', value: 'completed' },
  { label: '已暂停', value: 'paused' },
  { label: '已阻塞', value: 'blocked' },
  { label: '等待中', value: 'waiting' },
  { label: '已停止', value: 'stopped' },
  { label: '已取消', value: 'cancelled' },
]

const priorityOptions = [
  { label: '高优先级', value: 'high' },
  { label: '中优先级', value: 'medium' },
  { label: '低优先级', value: 'low' },
]

const priorityColors: Record<string, 'error' | 'warning' | 'success'> = {
  high: 'error',
  medium: 'warning',
  low: 'success',
}

const priorityLabels: Record<string, string> = {
  high: '高',
  medium: '中',
  low: '低',
}

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

// Computed options
const tagOptions = computed(() => 
  tags.value.map(t => ({ label: t.name, value: t.id }))
)

// Phase 4: Parent task options filtered by project
const parentTaskOptions = computed(() => {
  // When creating a new task, use the selected project
  const projectId = form.value.project_id || currentProjectId.value
  if (!projectId) return []

  // Filter tasks by project and exclude completed tasks
  const filteredTasks = tasks.value.filter(
    t => t.project_id === projectId && t.status !== 'completed'
  )
  return [
    { label: '（根任务）', value: null },  // Option to be a root task
    ...filteredTasks.map(t => ({ label: t.title, value: t.id }))
  ]
})

const projectOptions = computed(() => 
  projects.value.map(p => ({ label: p.name, value: p.id }))
)

const columns = [
  {
    title: 'ID',
    key: 'id',
    width: 60,
  },
  {
    title: '标题',
    key: 'title',
    render(row: Task) {
      return h('span', {
        style: 'cursor: pointer; color: #2080f0;',
        onClick: () => router.push({ name: 'detail', params: { id: row.id } }),
      }, row.title)
    },
  },
  {
    title: '项目',
    key: 'project_id',
    width: 100,
    render(row: Task) {
      const project = projects.value.find(p => p.id === row.project_id)
      return h(NTag, { type: 'info', size: 'small' }, { default: () => project?.name || '未分类' })
    },
  },
  {
    title: '优先级',
    key: 'priority',
    width: 80,
    render(row: Task) {
      return h(NTag, { type: priorityColors[row.priority] || 'warning', size: 'small' }, 
        { default: () => priorityLabels[row.priority] || row.priority }
      )
    },
  },
  {
    title: '状态',
    key: 'status',
    width: 120,
    render(row: Task) {
      // Phase 4: Show blocked badge if task is blocked
      if (row.is_blocked && row.status === 'pending') {
        return h('div', { style: 'display: flex; align-items: center; gap: 4px;' }, [
          h(NTag, { type: 'warning', size: 'small' }, { default: () => '等待父任务' }),
        ])
      }
      return h(NTag, { type: statusColors[row.status] || 'default', size: 'small' },
        { default: () => statusLabels[row.status] || row.status }
      )
    },
  },
  {
    title: '进度',
    key: 'progress',
    width: 120,
    render(row: Task) {
      return h('div', { style: 'display: flex; align-items: center; gap: 8px;' }, [
        h('div', { 
          style: 'flex: 1; height: 6px; background: #eee; border-radius: 3px; overflow: hidden;' 
        }, [
          h('div', { 
            style: `width: ${row.progress}%; height: 100%; background: ${row.progress === 100 ? '#18a058' : '#2080f0'}; border-radius: 3px;` 
          })
        ]),
        h('span', { style: 'font-size: 12px; color: #666;' }, `${row.progress}%`)
      ])
    },
  },
  {
    title: '负责人',
    key: 'owner',
    width: 100,
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 180,
    render(row: Task) {
      return new Date(row.created_at).toLocaleString('zh-CN')
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 280,
    render(row: Task) {
      // Phase 4: Disable status change if blocked by parent
      const isBlocked = row.is_blocked && row.status === 'pending'
      const disabled = isBlocked

      return h('div', { style: 'display: flex; gap: 4px; flex-wrap: nowrap; align-items: center;' }, [
        h(NButton, {
          size: 'small',
          onClick: () => openEditModal(row)
        }, { default: () => '编辑' }),
        h(NSelect, {
          size: 'small',
          options: statusOptions,
          value: row.status,
          style: 'width: 90px',
          disabled: disabled,
          disabledTip: isBlocked ? '等待父任务完成' : undefined,
          onUpdateValue: (status: string) => handleStatusChange(row, status)
        }),
        h(NButton, {
          size: 'small',
          type: 'error',
          onClick: () => handleDelete(row.id)
        }, { default: () => '删除' }),
      ])
    },
  },
]

const loadTasks = async () => {
  loading.value = true
  try {
    tasks.value = await taskApi.getTasks(
      statusFilter.value || undefined,
      priorityFilter.value || undefined,
      tagFilter.value || undefined
    )
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

const loadProjects = async () => {
  try {
    projects.value = await projectApi.getProjects()
  } catch (e) {
    console.error('加载项目失败', e)
  }
}

const handleCreate = async () => {
  if (!form.value.title) {
    message.error('请输入标题')
    return
  }
  creating.value = true
  try {
    const task = await taskApi.createTask(form.value)
    // Add tags if selected
    if (form.value.tag_ids && form.value.tag_ids.length > 0) {
      for (const tagId of form.value.tag_ids) {
        await tagApi.addTagToTask(task.id, tagId)
      }
    }
    message.success('创建成功')
    showCreateModal.value = false
    form.value = { title: '', description: '', owner: '', parent_id: null, project_id: 1, priority: 'medium', tag_ids: [] }
    await loadTasks()
  } catch (e) {
    message.error('创建失败')
  } finally {
    creating.value = false
  }
}

const openEditModal = (task: Task) => {
  editingId.value = task.id
  editForm.value = {
    title: task.title,
    description: task.description || '',
    owner: task.owner || '',
    parent_id: task.parent_id,
    project_id: task.project_id,
    priority: task.priority,
  }
  showEditModal.value = true
}

const handleUpdate = async () => {
  if (!editingId.value) return
  updating.value = true
  try {
    await taskApi.updateTask(editingId.value, editForm.value)
    message.success('更新成功')
    showEditModal.value = false
    await loadTasks()
  } catch (e) {
    message.error('更新失败')
  } finally {
    updating.value = false
  }
}

const handleStatusChange = async (task: Task, newStatus: string) => {
  try {
    await taskApi.updateStatus(task.id, newStatus)
    message.success(`已改为 ${statusLabels[newStatus]}`)
    await loadTasks()
  } catch (e) {
    message.error('状态更新失败')
  }
}

const handleDelete = async (id: number) => {
  try {
    await taskApi.deleteTask(id)
    message.success('删除成功')
    await loadTasks()
  } catch (e) {
    message.error('删除失败')
  }
}

onMounted(() => {
  loadTasks()
  loadTags()
  loadProjects()
})
</script>

<style scoped>
.task-list {
  max-width: 1400px;
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
