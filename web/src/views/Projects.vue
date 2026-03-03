<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { NCard, NButton, NModal, NForm, NFormItem, NInput, NSpace, NDataTable, NTag, NPopconfirm, useMessage } from 'naive-ui'
import { projectApi, type Project, type ProjectCreate } from '../api/tasks'

const message = useMessage()
const projects = ref<Project[]>([])
const loading = ref(false)
const showModal = ref(false)
const editingProject = ref<Project | null>(null)
const formData = ref<ProjectCreate>({
  name: '',
  description: ''
})

const columns = [
  {
    title: 'ID',
    key: 'id',
    width: 60
  },
  {
    title: '名称',
    key: 'name'
  },
  {
    title: '描述',
    key: 'description'
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: (row: Project) => {
      return h(NTag, { type: row.status === 'active' ? 'success' : 'default' }, { default: () => row.status })
    }
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 180,
    render: (row: Project) => new Date(row.created_at).toLocaleString('zh-CN')
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    render: (row: Project) => {
      return h(NSpace, { size: 'small' }, { 
        default: () => [
          h(NButton, { size: 'small', onClick: () => editProject(row) }, { default: () => '编辑' }),
          h(NPopconfirm, { onPositiveClick: () => deleteProject(row.id) }, {
            trigger: () => h(NButton, { size: 'small', type: 'error' }, { default: () => '删除' }),
            default: () => '确定删除此项目？'
          })
        ]
      })
    }
  }
]

import { h } from 'vue'

const fetchProjects = async () => {
  loading.value = true
  try {
    projects.value = await projectApi.getProjects()
  } catch (e: any) {
    message.error('获取项目列表失败: ' + e.message)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  editingProject.value = null
  formData.value = { name: '', description: '' }
  showModal.value = true
}

const editProject = (project: Project) => {
  editingProject.value = project
  formData.value = { name: project.name, description: project.description || '' }
  showModal.value = true
}

const handleSubmit = async () => {
  try {
    if (editingProject.value) {
      await projectApi.updateProject(editingProject.value.id, formData.value)
      message.success('项目更新成功')
    } else {
      await projectApi.createProject(formData.value)
      message.success('项目创建成功')
    }
    showModal.value = false
    fetchProjects()
  } catch (e: any) {
    message.error('操作失败: ' + e.message)
  }
}

const deleteProject = async (id: number) => {
  try {
    await projectApi.deleteProject(id)
    message.success('项目删除成功')
    fetchProjects()
  } catch (e: any) {
    message.error('删除失败: ' + e.message)
  }
}

onMounted(() => {
  fetchProjects()
})
</script>

<template>
  <div class="projects-page">
    <NCard title="项目管理">
      <template #header-extra>
        <NButton type="primary" @click="openCreateModal">新建项目</NButton>
      </template>
      
      <NDataTable
        :columns="columns"
        :data="projects"
        :loading="loading"
        :bordered="false"
      />
    </NCard>

    <NModal v-model:show="showModal" preset="card" :title="editingProject ? '编辑项目' : '新建项目'" style="width: 500px;">
      <NForm :model="formData" label-placement="left">
        <NFormItem label="名称" required>
          <NInput v-model:value="formData.name" placeholder="请输入项目名称" />
        </NFormItem>
        <NFormItem label="描述">
          <NInput v-model:value="formData.description" type="textarea" placeholder="请输入项目描述" :rows="3" />
        </NFormItem>
      </NForm>
      <template #footer>
        <NSpace justify="end">
          <NButton @click="showModal = false">取消</NButton>
          <NButton type="primary" @click="handleSubmit">确定</NButton>
        </NSpace>
      </template>
    </NModal>
  </div>
</template>

<style scoped>
.projects-page {
  padding: 20px;
}
</style>
