<template>
  <div class="strategy-edit-view" v-loading="loading">
    <div class="page-header">
      <div>
        <p class="eyebrow">创作者中心</p>
        <h1>{{ isEdit ? '编辑攻略' : '发布攻略' }}</h1>
        <p class="subtext">支持富文本、图片与视频上传（需先保存再上传媒体）</p>
      </div>
      <div class="actions">
        <el-button @click="router.back()">返回</el-button>
        <el-button type="primary" :icon="Check" :loading="saving" @click="handleSubmit">
          {{ isEdit ? '保存修改' : '发布攻略' }}
        </el-button>
      </div>
    </div>

    <el-alert
      v-if="currentStrategy"
      :title="`当前状态：${statusLabel}`"
      :type="statusType"
      show-icon
      :closable="false"
      class="status-alert"
    >
      <template #description>
        <span v-if="latestRejectReason">拒绝原因：{{ latestRejectReason }}</span>
        <span v-else>审核信息将显示在此处</span>
      </template>
    </el-alert>

    <el-card shadow="never" class="form-card">
      <el-form label-width="100px" :model="form" class="strategy-form">
        <el-form-item label="标题">
          <el-input v-model="form.title" maxlength="100" show-word-limit placeholder="请输入攻略标题" />
        </el-form-item>

        <el-form-item label="关联游戏">
          <el-select
            v-model="form.game"
            filterable
            clearable
            placeholder="请选择游戏"
            :loading="gamesLoading"
            style="width: 100%"
          >
            <el-option
              v-for="game in games"
              :key="game.id"
              :label="game.name"
              :value="game.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="内容">
          <div class="editor">
            <div id="vditor" ref="vditorEl" class="vditor-host"></div>
          </div>
        </el-form-item>

        <el-form-item label="媒体资源">
          <div class="media-section">
            <div class="upload-block">
              <p class="label">图片</p>
              <el-upload
                v-if="strategyId"
                action=""
                list-type="picture-card"
                :http-request="(opts) => handleUpload(opts, 'image')"
                :on-remove="(file) => handleRemove(file, 'image')"
                :file-list="imageFiles"
                :show-file-list="true"
              >
                <el-icon><Plus /></el-icon>
                <template #tip>
                  <div class="el-upload__tip">JPG/PNG，单个不超过 5MB</div>
                </template>
              </el-upload>
              <div v-else class="upload-disabled">请先保存攻略，再上传图片</div>
            </div>

            <div class="upload-block">
              <p class="label">视频</p>
              <el-upload
                v-if="strategyId"
                action=""
                :http-request="(opts) => handleUpload(opts, 'video')"
                :on-remove="(file) => handleRemove(file, 'video')"
                :file-list="videoFiles"
                :limit="3"
              >
                <el-button type="primary" plain>上传视频</el-button>
                <template #tip>
                  <div class="el-upload__tip">MP4 等常见格式，建议 &lt; 100MB；分片未实现则直接上传</div>
                </template>
              </el-upload>
              <div v-else class="upload-disabled">请先保存攻略，再上传视频</div>
            </div>
          </div>
        </el-form-item>

        <el-form-item v-if="isEdit" label="数据概览">
          <div class="stats">
            <div class="stat">
              <span class="stat-label">曝光量</span>
              <span class="stat-value">{{ currentStrategy?.view_count ?? 0 }}</span>
            </div>
            <div class="stat">
              <span class="stat-label">点赞数</span>
              <span class="stat-value">{{ currentStrategy?.like_count ?? 0 }}</span>
            </div>
            <div class="stat">
              <span class="stat-label">收藏数</span>
              <span class="stat-value">{{ currentStrategy?.collect_count ?? 0 }}</span>
            </div>
          </div>
        </el-form-item>

        <el-form-item v-if="isEdit" label="危险操作">
          <el-button type="danger" plain @click="handleDelete" :loading="deleting">删除攻略</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Check } from '@element-plus/icons-vue'
import { getGameList } from '@/api/game'
import { createStrategy, updateStrategy, getStrategyDetail, deleteStrategy, uploadMedia, deleteMedia } from '@/api/content'
import { request } from '@/utils/request'
import type { Strategy, MediaAsset } from '@/types/content'
import type Vditor from 'vditor'
import 'vditor/dist/index.css'

const router = useRouter()
const route = useRoute()
const isEdit = computed(() => !!route.params.id)
const strategyId = computed(() => (route.params.id ? Number(route.params.id) : null))

const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const gamesLoading = ref(false)

const games = ref<any[]>([])
const currentStrategy = ref<Strategy | null>(null)
const imageFiles = ref<any[]>([])
const videoFiles = ref<any[]>([])

const form = reactive({
  title: '',
  game: null as number | null,
  content: ''
})

const vditorEl = ref<HTMLElement | null>(null)
const vditor = ref<Vditor | null>(null)
let VditorCtor: any = null

const ensureVditor = async () => {
  if (VditorCtor) return VditorCtor
  const mod = await import('vditor')
  VditorCtor = mod.default
  return VditorCtor
}

const initEditor = async (initial = '') => {
  const VCtor = await ensureVditor()
  vditor.value = new VCtor('vditor', {
    height: 400,
    placeholder: '请输入攻略内容...',
    mode: 'wysiwyg',
    toolbarConfig: { pin: true },
    customWysiwygToolbar: () => {}, // 避免空函数导致的异常
    cache: { enable: false },
    preview: { actions: ['desktop', 'tablet', 'mobile'] },
    toolbar: [
      'headings',
      'bold',
      'italic',
      'strike',
      '|',
      'list',
      'ordered-list',
      'check',
      'quote',
      '|',
      'link',
      'table',
      'line',
      'emoji',
      'code',
      'inline-code',
      '|',
      'undo',
      'redo',
      'fullscreen',
      'preview'
    ],
    upload: {
      accept: 'image/*,video/*',
      multiple: true,
      handler: async (files) => {
        if (!strategyId.value) {
          ElMessage.warning('请先保存攻略，再上传媒体')
          return
        }
        for (const file of files) {
          const type = file.type.startsWith('video') ? 'video' : 'image'
          try {
            const resp = await uploadMedia(file as File, type, strategyId.value)
            const asset = resp as unknown as MediaAsset
            const url = (asset as any).url || ''
            if (type === 'image') {
              vditor.value?.insertValue(`![${file.name}](${url})\n`)
            } else {
              vditor.value?.insertValue(`[视频](${url})\n`)
            }
          } catch (err: any) {
            ElMessage.error(err?.message || '上传失败')
          }
        }
      }
    },
    input(value) {
      form.content = value
    },
    after() {
      if (initial) {
        vditor.value?.setValue(initial)
        form.content = initial
      }
    }
  })
}

const fetchGames = async () => {
  gamesLoading.value = true
  try {
    const all: any[] = []
    let nextUrl: string | null = null

    // 第一次请求
    const data = await getGameList({ page_size: 200, ordering: 'name' })
    if (data.results?.length) {
      all.push(...data.results)
      nextUrl = data.next || null
    }

    // 按 next 继续拉取，直到没有下一页
    while (nextUrl) {
      const resp = await request.get(nextUrl)
      if (resp?.results?.length) {
        all.push(...resp.results)
        nextUrl = resp.next || null
      } else {
        break
      }
    }

    games.value = all
  } catch (e: any) {
    console.error(e)
  } finally {
    gamesLoading.value = false
  }
}

const mapMediaToFile = (asset: MediaAsset) => ({
  name: asset.url?.split('/').pop(),
  url: asset.url,
  status: 'success',
  assetId: asset.id
})

const loadDetail = async () => {
  if (!strategyId.value) return
  loading.value = true
  try {
    const data = await getStrategyDetail(strategyId.value)
    currentStrategy.value = data as Strategy
    form.title = data.title
    form.game = data.game?.id || (data as any).game || null
    await nextTick()
    if (vditor.value) {
      vditor.value.setValue(data.content || '')
    } else {
      await initEditor(data.content || '')
    }
    const images = (data.media_assets || []).filter((m: any) => m.type === 'image')
    const videos = (data.media_assets || []).filter((m: any) => m.type === 'video')
    imageFiles.value = images.map(mapMediaToFile)
    videoFiles.value = videos.map(mapMediaToFile)
  } catch (e: any) {
    ElMessage.error(e?.message || '加载攻略失败')
  } finally {
    loading.value = false
  }
}

const validate = () => {
  if (!form.title.trim()) {
    ElMessage.warning('请输入标题')
    return false
  }
  if (!form.game) {
    ElMessage.warning('请选择关联游戏')
    return false
  }
  const contentVal = vditor.value?.getValue() || form.content
  if (!contentVal.trim()) {
    ElMessage.warning('请输入攻略内容')
    return false
  }
  return true
}

const statusLabel = computed(() => {
  const status = currentStrategy.value?.status
  if (status === 'approved') return '已通过'
  if (status === 'rejected') return '已拒绝'
  if (status === 'pending') return '待审核'
  return '未提交'
})

const statusType = computed(() => {
  const status = currentStrategy.value?.status
  if (status === 'approved') return 'success'
  if (status === 'rejected') return 'error'
  if (status === 'pending') return 'warning'
  return 'info'
})

const latestRejectReason = computed(() => {
  if (!currentStrategy.value?.reviews?.length) return ''
  const rejected = (currentStrategy.value as any).reviews.find((r: any) => r.decision === 'rejected' && r.reason)
  return rejected?.reason || ''
})

const handleSubmit = async () => {
  if (!validate()) return
  saving.value = true
  try {
    if (isEdit.value && strategyId.value) {
      const contentVal = vditor.value?.getHTML?.() || vditor.value?.getValue() || form.content
      await updateStrategy(strategyId.value, {
        title: form.title,
        content: contentVal,
        game: form.game as number
      })
      ElMessage.success('保存成功')
    } else {
      const contentVal = vditor.value?.getHTML?.() || vditor.value?.getValue() || form.content
      const res = await createStrategy({
        title: form.title,
        content: contentVal,
        game: form.game as number
      })
      ElMessage.success('发布成功，待审核')
      router.replace(`/strategies/edit/${(res as any).id}`)
      return
    }
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

const handleUpload = async (options: any, type: 'image' | 'video') => {
  const { file, onSuccess, onError, onProgress } = options
  if (!strategyId.value) {
    onError(new Error('请先保存攻略再上传'))
    return
  }
  try {
    const resp = await uploadMedia(file as File, type, strategyId.value)
    const asset = resp as unknown as MediaAsset
    const fileItem = mapMediaToFile(asset)
    if (type === 'image') {
      imageFiles.value.push(fileItem)
    } else {
      videoFiles.value.push(fileItem)
    }
    onSuccess(asset)
  } catch (e: any) {
    onError(e)
  }
}

const handleRemove = async (file: any, type: 'image' | 'video') => {
  if (!file.assetId) return
  try {
    await deleteMedia(file.assetId)
    if (type === 'image') {
      imageFiles.value = imageFiles.value.filter((f) => f.assetId !== file.assetId)
    } else {
      videoFiles.value = videoFiles.value.filter((f) => f.assetId !== file.assetId)
    }
    ElMessage.success('已删除')
  } catch (e: any) {
    ElMessage.error(e?.message || '删除失败')
  }
}

const handleDelete = async () => {
  if (!strategyId.value) return
  try {
    await ElMessageBox.confirm('确定删除该攻略吗？操作不可恢复', '提示', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    deleting.value = true
    await deleteStrategy(strategyId.value)
    ElMessage.success('已删除')
    router.push('/strategies/list')
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e?.message || '删除失败')
    }
  } finally {
    deleting.value = false
  }
}

onMounted(async () => {
  await fetchGames()
  await initEditor()
  if (isEdit.value) {
    await loadDetail()
  }
})

onBeforeUnmount(() => {
  vditor.value?.destroy?.()
})
</script>

<style scoped lang="scss">
.strategy-edit-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .eyebrow {
    margin: 0;
    color: var(--el-color-primary);
    font-weight: 700;
  }

  h1 {
    margin: 4px 0;
  }

  .subtext {
    margin: 0;
    color: var(--el-text-color-secondary);
  }
}

.form-card {
  border-radius: 14px;
}

.strategy-form {
  .editor {
    width: 100%;

    .toolbar {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 8px;

      .tips {
        color: var(--el-text-color-secondary);
        margin-left: auto;
        font-size: 13px;
      }
    }

    .editor-area {
      min-height: 240px;
      border: 1px solid var(--el-border-color);
      border-radius: 10px;
      padding: 12px;
      outline: none;
      line-height: 1.6;
      background: var(--el-bg-color);
    }
  }

  .media-section {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 16px;

    .upload-block {
      background: var(--el-fill-color-light);
      padding: 12px;
      border-radius: 12px;

      .label {
        margin: 0 0 6px;
        font-weight: 700;
      }

      .upload-disabled {
        color: var(--el-text-color-secondary);
        padding: 12px;
        border: 1px dashed var(--el-border-color);
        border-radius: 10px;
      }
    }
  }

  .stats {
    display: flex;
    gap: 24px;

    .stat {
      display: flex;
      flex-direction: column;
      gap: 6px;

      .stat-label {
        color: var(--el-text-color-secondary);
      }

      .stat-value {
        font-size: 18px;
        font-weight: 700;
      }
    }
  }
}
</style>
