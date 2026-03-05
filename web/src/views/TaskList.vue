<template>
  <div class="task-list">
    <div class="header">
      <h1>任务列表</h1>
      <n-button type="primary" @click="showCreateModal = true">
        新建任务
      </n-button>
    </div>

    <n-space style="margin-bottom: 16px;">
      <n-popselect v-model:value="statusFilter" :options="statusOptions" multiple trigger="click" @update:value="applyFilters">
        <n-button>
          筛选状态 {{ statusFilter.length > 0 ? `(${statusFilter.length})` : '' }}
        </n-button>
      </n-popselect>
      <n-popselect v-model:value="priorityFilter" :options="priorityOptions" multiple trigger="click" @update:value="applyFilters">
        <n-button>
          筛选优先级 {{ priorityFilter.length > 0 ? `(${priorityFilter.length})` : '' }}
        </n-button>
      </n-popselect>
      <n-popselect v-model:value="tagFilter" :options="tagOptions" multiple trigger="click" @update:value="applyFilters">
        <n-button>
          筛选标签 {{ tagFilter.length > 0 ? `(${tagFilter.length})` : '' }}
        </n-button>
      </n-popselect>
      <n-popselect v-model:value="projectFilter" :options="projectFilterOptions" multiple trigger="click" @update:value="applyFilters">
        <n-button>
          筛选项目 {{ projectFilter.length > 0 ? `(${projectFilter.length})` : '' }}
        </n-button>
      </n-popselect>
      <n-button @click="loadTasks">刷新</n-button>
      <n-button @click="exportToExcel">导出 Excel</n-button>
      <n-radio-group v-model:value="viewMode" style="margin-left: auto;">
        <n-radio-button value="list">列表</n-radio-button>
        <n-radio-button value="kanban">看板</n-radio-button>
        <n-radio-button value="tree">树</n-radio-button>
      </n-radio-group>
    </n-space>

    <!-- 看板视图 -->
    <div v-if="viewMode === 'kanban'" class="kanban-board">
      <n-scrollbar x-scrollable>
        <div class="kanban-columns">
          <div v-for="col in kanbanColumns" :key="col.status" class="kanban-column">
            <div class="column-header" :style="{ borderColor: col.color }">
              <span class="column-title">{{ col.label }}</span>
              <n-tag :bordered="false" size="small">{{ col.tasks.length }}</n-tag>
            </div>
            <draggable
              v-model="col.tasks"
              group="tasks"
              item-key="id"
              class="column-tasks"
              :disabled="col.status !== 'blocked'"
              @change="(evt: any) => onDragEnd(evt, col.status)"
            >
              <template #item="{ element }: { element: Task }">
                <div class="task-card" :class="{ 'is-blocked': element.is_blocked }">
                  <div class="task-header">
                    <div class="task-title">{{ element.title }}</div>
                    <n-tag v-if="element.is_blocked" type="error" size="small" class="block-badge">阻塞</n-tag>
                  </div>
                  <n-space size="small">
                    <n-tag v-if="element.priority === 'high'" type="error" size="small">高</n-tag>
                    <n-tag v-if="element.priority === 'medium'" type="warning" size="small">中</n-tag>
                    <n-tag v-if="element.priority === 'low'" type="success" size="small">低</n-tag>
                    <n-tag v-if="element.project_id" type="info" size="small">{{ getProjectName(element.project_id) }}</n-tag>
                  </n-space>
                  <div v-if="element.is_blocked" class="block-hint">等待前置任务完成</div>
                </div>
              </template>
            </draggable>
          </div>
        </div>
      </n-scrollbar>
    </div>

    <!-- 列表视图 -->
    <n-data-table
      v-else-if="viewMode === 'list'"
      :columns="columns"
      :data="tasks"
      :loading="loading"
      :row-key="(row: Task) => row.id"
      :pagination="false"
    />

    <!-- 树视图 -->
    <div v-else class="tree-view">
      <n-scrollbar style="max-height: 600px;">
        <n-tree
          :data="treeData"
          :default-expand-all="false"
          :selectable="false"
          key-field="key"
          label-field="label"
          children-field="children"
        />
      </n-scrollbar>
    </div>

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
        <n-form-item label="前置任务">
          <n-select
            v-model:value="form.depends_on"
            :options="dependencyTaskOptions"
            multiple
            placeholder="选择前置任务（可选）"
            clearable
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
        <n-form-item label="前置任务">
          <n-select
            v-model:value="editForm.depends_on"
            :options="editDependencyTaskOptions"
            multiple
            placeholder="选择前置任务（可选）"
            clearable
            style="width: 100%"
          />
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
import { ref, onMounted, h, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  NButton, NDataTable, NSpace, NModal, NForm, NFormItem,
  NInput, NSelect, NTag, NIcon, NPopselect, NRadioGroup, NRadioButton,
  NScrollbar, NTree, useMessage
} from 'naive-ui'
import { taskApi, tagApi, projectApi, Task, TaskCreate, TaskUpdate, Tag, Project } from '../api/tasks'
import * as XLSX from 'xlsx'
import {
  CreateOutline,
  TrashOutline,
  EllipsisVerticalOutline,
} from '@vicons/ionicons5'
import draggable from 'vuedraggable'

const router = useRouter()
const route = useRoute()

const searchQuery = computed(() => route.query.q as string | undefined)
const message = useMessage()

const tasks = ref<Task[]>([])
const tags = ref<Tag[]>([])
const projects = ref<Project[]>([])
const loading = ref(false)
const statusFilter = ref<string[]>([])
const priorityFilter = ref<string[]>([])
const tagFilter = ref<number[]>([])
const projectFilter = ref<number[]>([])
const showCreateModal = ref(false)
const showEditModal = ref(false)
const creating = ref(false)
const updating = ref(false)

// 看板视图
const viewMode = ref<'list' | 'kanban' | 'tree'>('list')

const form = ref<TaskCreate>({
  title: '',
  description: '',
  owner: '',
  parent_id: null,
  project_id: 1,  // Default to "未分类"
  priority: 'medium',
  tag_ids: [],
  depends_on: [],
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
  depends_on: [],
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

// 看板视图列
const kanbanColumns = computed(() => {
  const cols = [
    { status: 'pending', label: '待处理', color: '#64748b', tasks: [] as Task[] },
    { status: 'in_progress', label: '进行中', color: '#3b82f6', tasks: [] as Task[] },
    { status: 'completed', label: '已完成', color: '#22c55e', tasks: [] as Task[] },
    { status: 'paused', label: '暂停', color: '#f59e0b', tasks: [] as Task[] },
    { status: 'blocked', label: '阻塞', color: '#ef4444', tasks: [] as Task[] },
    { status: 'waiting', label: '等待中', color: '#8b5cf6', tasks: [] as Task[] },
  ]
  const filtered = tasks.value
  cols.forEach(col => {
    col.tasks = filtered.filter(t => t.status === col.status)
  })
  return cols
})

// 树视图数据
interface TreeNode {
  key: string
  label: string
  children?: TreeNode[]
}

const treeData = computed(() => {
  const result: TreeNode[] = []

  // 按项目分组
  projects.value.forEach(project => {
    const projectTasks = tasks.value.filter(t => t.project_id === project.id)
    if (projectTasks.length === 0) return

    // 找出根任务（没有parent_id的）
    const rootTasks = projectTasks.filter(t => !t.parent_id)

    // 递归构建任务树
    const buildTaskTree = (taskList: Task[]): TreeNode[] => {
      return taskList.map(task => {
        const children = projectTasks.filter(t => t.parent_id === task.id)
        const node: TreeNode = {
          key: `task-${task.id}`,
          label: `${task.title} (${priorityLabels[task.priority] || task.priority})`,
        }
        if (children.length > 0) {
          node.children = buildTaskTree(children)
        }
        return node
      })
    }

    // 构建项目节点
    const projectNode: TreeNode = {
      key: `project-${project.id}`,
      label: project.name,
      children: buildTaskTree(rootTasks),
    }

    result.push(projectNode)
  })

  return result
})

const getProjectName = (projectId: number) => {
  const p = projects.value.find(p => p.id === projectId)
  return p?.name || '未分类'
}

const onDragEnd = async (evt: any, newStatus: string) => {
  if (evt.added) {
    const task = evt.added.element as Task
    await taskApi.updateStatus(task.id, newStatus)
    loadTasks()
  }
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

// Phase 2: Dependency task options (create modal) - same project, exclude self
const dependencyTaskOptions = computed(() => {
  const projectId = form.value.project_id
  if (!projectId) return []

  // Filter tasks by project (can include completed tasks for dependency)
  return tasks.value
    .filter(t => t.project_id === projectId)
    .map(t => ({ label: t.title, value: t.id }))
})

// Phase 2: Dependency task options (edit modal) - same project, exclude editing task
const editDependencyTaskOptions = computed(() => {
  const projectId = editForm.value.project_id
  if (!projectId || !editingId.value) return []

  // Filter tasks by project, exclude the current editing task
  return tasks.value
    .filter(t => t.project_id === projectId && t.id !== editingId.value)
    .map(t => ({ label: t.title, value: t.id }))
})

const projectOptions = computed(() =>
  projects.value.map(p => ({ label: p.name, value: p.id }))
)

const projectFilterOptions = computed(() =>
  projects.value.map(p => ({ label: p.name, value: p.id }))
)

const allTasks = ref<Task[]>([])

const applyFilters = () => {
  let filtered = [...allTasks.value]

  if (statusFilter.value.length > 0) {
    filtered = filtered.filter(t => statusFilter.value.includes(t.status))
  }

  if (priorityFilter.value.length > 0) {
    filtered = filtered.filter(t => priorityFilter.value.includes(t.priority))
  }

  if (projectFilter.value.length > 0) {
    filtered = filtered.filter(t => projectFilter.value.includes(t.project_id))
  }

  // Tag filtering - check if task has any of the selected tags (via tag_ids if available)
  if (tagFilter.value.length > 0) {
    // Tasks have tag_ids property in the response
    filtered = filtered.filter(t => {
      const taskTagIds = (t as any).tag_ids || []
      return tagFilter.value.some(tagId => taskTagIds.includes(tagId))
    })
  }

  tasks.value = filtered
}

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
      // Phase 3: Show blocked status if task is blocked by dependency
      if (row.is_blocked) {
        return h('div', { style: 'display: flex; align-items: center; gap: 4px;' }, [
          h(NTag, { type: 'error', size: 'small' }, { default: () => '阻塞' }),
          h('span', { style: 'font-size: 12px; color: #666;' }, '等待前置任务'),
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
    width: 110,
    render(row: Task) {
      return h('div', { style: 'display: flex; align-items: center; gap: 8px;' }, [
        h('div', {
          style: 'width: 80px; height: 6px; background: #eee; border-radius: 3px; overflow: hidden; flex-shrink: 0;'
        }, [
          h('div', {
            style: `width: ${row.progress}%; height: 100%; background: ${row.progress === 100 ? '#18a058' : '#2080f0'}; border-radius: 3px;`
          })
        ]),
        h('span', { style: 'font-size: 12px; color: #666; white-space: nowrap;' }, `${row.progress}%`)
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
    allTasks.value = await taskApi.getTasks(searchQuery.value)
    applyFilters()
  } catch (e) {
    message.error('加载任务失败')
  } finally {
    loading.value = false
  }
}

// Watch for route query changes (search)
watch(() => route.query.q, () => {
  loadTasks()
})

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
  let task = null
  try {
    task = await taskApi.createTask(form.value)
  } catch (e) {
    message.error('创建失败')
    creating.value = false
    return
  }

  // 任务创建成功，尝试添加标签
  try {
    if (form.value.tag_ids && form.value.tag_ids.length > 0) {
      for (const tagId of form.value.tag_ids) {
        await tagApi.addTagToTask(task.id, tagId)
      }
    }
    message.success('创建成功')
  } catch (e) {
    message.warning('创建成功，但标签添加失败')
  }

  showCreateModal.value = false
  form.value = { title: '', description: '', owner: '', parent_id: null, project_id: 1, priority: 'medium', tag_ids: [], depends_on: [] }
  await loadTasks()
  creating.value = false
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

// 导出 Excel
const exportToExcel = () => {
  const data = tasks.value.map(task => {
    // 项目名称
    const project = projects.value.find(p => p.id === task.project_id)
    // 优先级中文
    const priorityMap: Record<string, string> = { high: '高', medium: '中', low: '低' }
    // 状态中文
    const statusMap: Record<string, string> = {
      pending: '待处理', in_progress: '进行中', completed: '已完成',
      paused: '暂停', blocked: '阻塞', waiting: '等待中'
    }
    // 父任务
    const parent = tasks.value.find(t => t.id === task.parent_id)
    // 标签
    const taskTags = task.tag_ids?.map((tid: number) => {
      const tag = tags.value.find(t => t.id === tid)
      return tag?.name || ''
    }).filter(Boolean).join(',') || '-'

    return {
      ID: task.id,
      标题: task.title,
      项目: project?.name || '未分类',
      优先级: priorityMap[task.priority] || task.priority,
      状态: statusMap[task.status] || task.status,
      进度: `${task.progress}%`,
      负责人: task.owner || '-',
      创建时间: task.created_at,
      父任务: parent?.title || '-',
      标签: taskTags
    }
  })

  const ws = XLSX.utils.json_to_sheet(data)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '任务')

  const now = new Date()
  const filename = `tasks_${now.getFullYear()}${String(now.getMonth()+1).padStart(2,'0')}${String(now.getDate()).padStart(2,'0')}_${String(now.getHours()).padStart(2,'0')}${String(now.getMinutes()).padStart(2,'0')}${String(now.getSeconds()).padStart(2,'0')}.xlsx`

  XLSX.writeFile(wb, filename)
}
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

/* 看板视图样式 */
.kanban-board {
  margin-top: 16px;
}

.kanban-columns {
  display: flex;
  gap: 16px;
  padding: 8px;
  min-height: 500px;
}

.kanban-column {
  min-width: 280px;
  max-width: 280px;
  background: #f1f5f9;
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  margin-bottom: 12px;
  border-bottom: 3px solid;
}

.column-title {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
}

.column-tasks {
  flex: 1;
  min-height: 100px;
}

.task-card {
  background: white;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 10px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  cursor: grab;
  transition: box-shadow 0.2s, transform 0.2s;
}

.task-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  transform: translateY(-2px);
}

.task-card:active {
  cursor: grabbing;
}

.task-title {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
  margin-bottom: 8px;
  word-break: break-word;
}
</style>
