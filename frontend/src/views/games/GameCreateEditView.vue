<template>
  <div class="game-create-edit-view">
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <span>{{ isEdit ? '编辑游戏' : '创建游戏' }}</span>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
        class="game-form"
      >
        <!-- 基本信息 -->
        <el-form-item label="游戏名称" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="请输入游戏名称"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="分类" prop="category">
          <el-select
            v-model="formData.category"
            placeholder="请选择游戏分类"
          >
            <el-option
              v-for="cat in GAME_CATEGORIES"
              :key="cat.value"
              :label="cat.label"
              :value="cat.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="发行商" prop="publisher">
          <el-select
            v-model="formData.publisher"
            placeholder="请选择发行商"
            filterable
            remote
            :remote-method="searchPublishers"
            :loading="publisherLoading"
          >
            <el-option
              v-for="pub in publishers"
              :key="pub.id"
              :label="pub.name"
              :value="pub.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="标签" prop="tag_ids">
          <el-select
            v-model="formData.tag_ids"
            placeholder="请选择标签"
            multiple
            filterable
            remote
            :remote-method="searchTags"
            :loading="tagLoading"
          >
            <el-option
              v-for="tag in tags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="发行日期" prop="release_date">
          <el-date-picker
            v-model="formData.release_date"
            type="date"
            placeholder="选择发行日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>

        <el-form-item label="上线时间" prop="online_time">
          <el-date-picker
            v-model="formData.online_time"
            type="date"
            placeholder="选择上线时间"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>

        <el-form-item label="版本号" prop="version">
          <el-input
            v-model="formData.version"
            placeholder="如: 1.0.0"
            maxlength="50"
          />
        </el-form-item>

        <el-form-item label="游戏描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="6"
            placeholder="请输入游戏描述"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>

        <!-- 封面图 -->
        <el-form-item label="封面图" prop="cover_image">
          <div class="image-upload-section">
            <el-upload
              v-model:file-list="coverImageList"
              action="#"
              :auto-upload="false"
              :limit="1"
              accept="image/*"
              list-type="picture-card"
              @change="handleCoverImageChange"
            >
              <template #default>
                <el-icon class="avatar-uploader-icon"><Plus /></el-icon>
              </template>
              <template #file="{ file }">
                <div>
                  <img :src="file.url" alt="cover" />
                  <span class="el-upload-list__item-actions">
                    <span
                      class="el-upload-list__item-preview"
                      @click="handlePictureCardPreview(file)"
                    >
                      <el-icon><ZoomIn /></el-icon>
                    </span>
                    <span
                      class="el-upload-list__item-delete"
                      @click="handleRemove(file)"
                    >
                      <el-icon><Delete /></el-icon>
                    </span>
                  </span>
                </div>
              </template>
            </el-upload>
            <p class="upload-tip">推荐尺寸: 400x600px, 支持 JPG/PNG</p>
          </div>
        </el-form-item>

        <!-- 游戏截图 -->
        <el-form-item label="游戏截图">
          <div class="screenshots-section">
            <div class="screenshots-upload">
              <el-upload
                v-model:file-list="screenshotsList"
                action="#"
                :auto-upload="false"
                :limit="10"
                accept="image/*"
                list-type="picture-card"
                multiple
                @change="handleScreenshotsChange"
              >
                <template #default>
                  <el-icon class="avatar-uploader-icon"><Plus /></el-icon>
                </template>
                <template #file="{ file }">
                  <div>
                    <img :src="file.url" alt="screenshot" />
                    <span class="el-upload-list__item-actions">
                      <span
                        class="el-upload-list__item-preview"
                        @click="handlePictureCardPreview(file)"
                      >
                        <el-icon><ZoomIn /></el-icon>
                      </span>
                      <span
                        class="el-upload-list__item-delete"
                        @click="handleRemoveScreenshot(file)"
                      >
                        <el-icon><Delete /></el-icon>
                      </span>
                    </span>
                  </div>
                </template>
              </el-upload>
              <p class="upload-tip">最多上传 10 张截图，推荐尺寸: 1280x720px</p>
            </div>

            <!-- 已上传的截图列表 -->
            <div v-if="existingScreenshots.length > 0" class="existing-screenshots">
              <h4>已上传的截图</h4>
              <el-row :gutter="16">
                <el-col v-for="(screenshot, index) in existingScreenshots" :key="screenshot.id" :xs="12" :sm="8" :md="6">
                  <div class="screenshot-item">
                    <img :src="screenshot.image_url" :alt="`screenshot-${index}`" />
                    <div class="screenshot-actions">
                      <el-button
                        type="danger"
                        size="small"
                        @click="deleteScreenshot(screenshot.id)"
                        :loading="deletingScreenshotIds.has(screenshot.id)"
                      >
                        删除
                      </el-button>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </div>
        </el-form-item>

        <!-- 操作按钮 -->
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            {{ isEdit ? '更新游戏' : '创建游戏' }}
          </el-button>
          <el-button @click="handleCancel">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 图片预览对话框 -->
    <el-dialog v-model="previewDialogVisible" title="图片预览">
      <img :src="previewImageUrl" alt="preview" style="width: 100%" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import {
  createGame,
  getGameDetail,
  uploadGameScreenshot,
  deleteGameScreenshot,
  getGameScreenshots,
  getPublishers,
  getGameTags
} from '@/api/game'
import { GAME_CATEGORIES } from '@/constants/categories'
import { Plus, Delete, ZoomIn } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, UploadFile } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const formRef = ref<FormInstance>()
const previewDialogVisible = ref(false)
const previewImageUrl = ref('')

const isEdit = computed(() => !!route.params.id)
const gameId = computed(() => Number(route.params.id) || null)

const formData = reactive({
  name: '',
  category: '',
  publisher: null as number | null,
  tag_ids: [] as number[],
  release_date: '',
  online_time: '',
  version: '',
  description: '',
  cover_image: null as File | null
})

const rules = {
  name: [{ required: true, message: '请输入游戏名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择游戏分类', trigger: 'change' }],
  publisher: [{ required: true, message: '请选择发行商', trigger: 'change' }]
}

const coverImageList = ref<UploadFile[]>([])
const screenshotsList = ref<UploadFile[]>([])
const existingScreenshots = ref<any[]>([])

const publishers = ref<any[]>([])
const tags = ref<any[]>([])
const publisherLoading = ref(false)
const tagLoading = ref(false)
const submitting = ref(false)
const deletingScreenshotIds = ref(new Set<number>())

// 搜索发行商
const searchPublishers = async (query: string) => {
  if (!query) {
    publishers.value = []
    return
  }
  publisherLoading.value = true
  try {
    const response = await getPublishers()
    const list = Array.isArray(response) ? response : response.results || []
    publishers.value = list.filter((p: any) =>
      p.name.toLowerCase().includes(query.toLowerCase())
    )
  } catch (error) {
    ElMessage.error('获取发行商列表失败')
  } finally {
    publisherLoading.value = false
  }
}

// 搜索标签
const searchTags = async (query: string) => {
  tagLoading.value = true
  try {
    const response = await getGameTags()
    const list = Array.isArray(response) ? response : response.results || []
    if (query) {
      tags.value = list.filter((t: any) =>
        t.name.toLowerCase().includes(query.toLowerCase())
      )
    } else {
      tags.value = list
    }
  } catch (error) {
    ElMessage.error('获取标签列表失败')
  } finally {
    tagLoading.value = false
  }
}

// 处理封面图变化
const handleCoverImageChange = (file: UploadFile) => {
  if (file.raw) {
    formData.cover_image = file.raw
  }
}

// 处理截图变化
const handleScreenshotsChange = () => {
  // 截图在提交时处理
}

// 删除封面图
const handleRemove = (file: UploadFile) => {
  formData.cover_image = null
  coverImageList.value = []
}

// 删除截图
const handleRemoveScreenshot = (file: UploadFile) => {
  const index = screenshotsList.value.findIndex(f => f.uid === file.uid)
  if (index > -1) {
    screenshotsList.value.splice(index, 1)
  }
}

// 删除已上传的截图
const deleteScreenshot = async (screenshotId: number) => {
  try {
    await ElMessageBox.confirm('确定要删除此截图吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    deletingScreenshotIds.value.add(screenshotId)
    await deleteGameScreenshot(screenshotId)
    existingScreenshots.value = existingScreenshots.value.filter(s => s.id !== screenshotId)
    ElMessage.success('删除成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  } finally {
    deletingScreenshotIds.value.delete(screenshotId)
  }
}

// 图片预览
const handlePictureCardPreview = (file: UploadFile) => {
  previewImageUrl.value = file.url || ''
  previewDialogVisible.value = true
}

// 获取游戏详情（编辑时）
const fetchGameDetail = async () => {
  if (!isEdit.value || !gameId.value) return

  try {
    const game = await getGameDetail(gameId.value)
    formData.name = game.name
    formData.category = game.category
    formData.publisher = game.publisher.id
    formData.tag_ids = game.tags.map(t => t.id)
    formData.release_date = game.release_date || ''
    formData.online_time = game.online_time || ''
    formData.version = game.version || ''
    formData.description = game.description || ''

    // 加载已上传的截图
    const screenshots = await getGameScreenshots(gameId.value)
    existingScreenshots.value = Array.isArray(screenshots) ? screenshots : screenshots.results || []
  } catch (error) {
    ElMessage.error('获取游戏详情失败')
    router.back()
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate()

  submitting.value = true

  try {
    const formDataObj = new FormData()
    formDataObj.append('name', formData.name)
    formDataObj.append('category', formData.category)
    formDataObj.append('publisher', String(formData.publisher))
    formDataObj.append('description', formData.description)

    if (formData.release_date) {
      formDataObj.append('release_date', formData.release_date)
    }
    if (formData.online_time) {
      formDataObj.append('online_time', formData.online_time)
    }
    if (formData.version) {
      formDataObj.append('version', formData.version)
    }

    // 添加标签
    formData.tag_ids.forEach(id => {
      formDataObj.append('tag_ids', String(id))
    })

    // 添加封面图
    if (formData.cover_image) {
      formDataObj.append('cover_image', formData.cover_image)
    }

    // 创建游戏
    const gameResponse = await createGame(formDataObj)
    const newGameId = gameResponse.id

    // 上传截图
    if (screenshotsList.value.length > 0) {
      for (let i = 0; i < screenshotsList.value.length; i++) {
        const file = screenshotsList.value[i]
        if (file.raw) {
          const screenshotFormData = new FormData()
          screenshotFormData.append('image', file.raw)
          screenshotFormData.append('order', String(i))
          screenshotFormData.append('title', `截图 ${i + 1}`)

          try {
            await uploadGameScreenshot(newGameId, screenshotFormData)
          } catch (error) {
            console.error(`上传截图 ${i + 1} 失败:`, error)
          }
        }
      }
    }

    ElMessage.success(isEdit.value ? '游戏更新成功' : '游戏创建成功')
    router.push(`/games/${newGameId}`)
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

// 取消
const handleCancel = () => {
  router.back()
}

onMounted(async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/auth/login')
    return
  }

  // 加载发行商和标签列表
  try {
    const publishersResponse = await getPublishers()
    publishers.value = Array.isArray(publishersResponse) ? publishersResponse : publishersResponse.results || []

    const tagsResponse = await getGameTags()
    tags.value = Array.isArray(tagsResponse) ? tagsResponse : tagsResponse.results || []
  } catch (error) {
    console.error('加载数据失败:', error)
  }

  // 如果是编辑模式，加载游戏详情
  if (isEdit.value) {
    await fetchGameDetail()
  }
})
</script>

<style scoped lang="scss">
.game-create-edit-view {
  padding: 20px;

  .main-card {
    max-width: 900px;
    margin: 0 auto;

    .card-header {
      font-size: 18px;
      font-weight: bold;
    }

    .game-form {
      margin-top: 20px;

      .image-upload-section {
        :deep(.el-upload-list__item) {
          border-radius: 8px;
        }

        .upload-tip {
          margin-top: 12px;
          color: var(--el-text-color-secondary);
          font-size: 12px;
        }
      }

      .screenshots-section {
        .screenshots-upload {
          margin-bottom: 24px;

          :deep(.el-upload-list__item) {
            border-radius: 8px;
          }

          .upload-tip {
            margin-top: 12px;
            color: var(--el-text-color-secondary);
            font-size: 12px;
          }
        }

        .existing-screenshots {
          h4 {
            margin-bottom: 16px;
            font-weight: bold;
          }

          .screenshot-item {
            position: relative;
            border-radius: 8px;
            overflow: hidden;
            background: var(--el-fill-color-light);

            img {
              width: 100%;
              height: 150px;
              object-fit: cover;
              display: block;
            }

            .screenshot-actions {
              position: absolute;
              bottom: 0;
              left: 0;
              right: 0;
              background: rgba(0, 0, 0, 0.7);
              padding: 8px;
              display: flex;
              justify-content: center;
              opacity: 0;
              transition: opacity 0.3s;

              &:hover {
                opacity: 1;
              }
            }

            &:hover .screenshot-actions {
              opacity: 1;
            }
          }
        }
      }
    }
  }
}

:deep(.avatar-uploader-icon) {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  text-align: center;
}
</style>

