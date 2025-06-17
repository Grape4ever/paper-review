<template>
    <div>
        <aside class="sidebar">
      <div class="logo">毕业论文格式审核</div>
      <ul class="menu">
        <div>
          <h2>文件上传</h2>
          <div class="upload-buttons">
            <!-- 多文件选择 -->
            <input
              ref="fileInput"
              type="file"
              @change="onFileChange"
              accept=".pdf,.doc,.docx,.zip"
              style="display: none"
              multiple
            />
            <!-- 文件夹选择 -->
            <input
              ref="folderInput"
              type="file"
              @change="onFolderChange"
              webkitdirectory
              directory
              style="display: none"
            />
            <button @click="triggerFileSelect">选择文件</button>
            <button @click="triggerFolderSelect">选择文件夹</button>
          </div>
          <div v-if="selectedFiles.length" class="selected-files">
            <h3>已选择的文件：</h3>
            <ul>
              <li v-for="(file, index) in selectedFiles" :key="index">
                {{ file.webkitRelativePath || file.name }}
              </li>
            </ul>
          </div>
          <button :disabled="!selectedFiles.length || loading" @click="uploadFiles" class="upload-btn">
            {{ loading ? "正在上传..." : "上传" }}
          </button>
          <div v-if="error" style="color: red; margin: 16px 0;">{{ error }}</div>
          <div v-if="uploadResult" style="margin: 16px 0; color:green;">{{ uploadResult }}</div>
        </div>
      </ul>
    </aside>
        <div class="stuLayout-container">
            <!-- 顶部提示栏 -->
            <div class="alert-bar">
            欢迎老师！
            </div>
            <!-- 添加参数输入组件 -->
            <div class="params-input">
                <h3>请输入文件命名参数设置</h3>
                <div class="input-group">
                    <label>学年度:</label>
                    <input v-model="params.academic_year" placeholder="例如: 2324"/>
                </div>
                <div class="input-group">
                    <label>省市代码:</label>
                    <input v-model="params.province_code" placeholder="例如: 44"/>
                </div>
                <div class="input-group">
                    <label>单位代码:</label>
                    <input v-model="params.unit_code" placeholder="例如: 14655"/>
                </div>
                <div class="input-group">
                    <label>专业代码:</label>
                    <input v-model="params.major_code" placeholder="例如: 080901"/>
                </div>
                <div class="input-group">
                    <button @click="reviewAllFiles" class="update-params-btn">启动</button>
                </div>
            </div>
            <div v-if="reviewDetails && reviewDetails.length" class="review-details">
            <h3>审核明细：</h3>
            <table>
                <thead>
                <tr>
                    <th>文件名</th>
                    <th>状态</th>
                    <th>信息</th>
                </tr>
                </thead>
                <tbody>
                <tr v-for="item in reviewDetails" :key="item.file">
                    <td>{{ item.file }}</td>
                    <td :style="{color: item.status === 'success' ? 'green' : 'red'}">
                    {{ item.status === 'success' ? '通过' : '失败' }}
                    </td>
                    <td><pre>{{ item.message }}</pre></td>
                </tr>
                </tbody>
            </table>
            </div>
        </div>

    </div>
    


</template>

<script setup>
import { ref } from "vue";

const fileInput = ref(null);
const folderInput = ref(null);
const selectedFiles = ref([]);
// const downloadUrl = ref("");
// const downloadName = ref("");
const error = ref("");
const loading = ref(false);
const uploadResult = ref("");
const reviewDetails = ref([]);
const params = ref({
    academic_year: "2324",
    province_code: "44",
    unit_code: "14655",
    major_code: "080901"
});

function triggerFileSelect() {
    fileInput.value?.click();
}

function triggerFolderSelect() {
    folderInput.value?.click();
}



function filterAllowed(files) {
  // 支持的扩展名
  const allow = /\.(pdf|doc|docx|zip)$/i;
  // 排重（同路径/文件名只留一个，优先后面的）
  const map = new Map();
  files.forEach(f => {
    const key = f.webkitRelativePath || f.name;
    if (allow.test(f.name)) map.set(key, f);
  });
  return Array.from(map.values());
}

function onFileChange(e) {
  selectedFiles.value = filterAllowed(Array.from(e.target.files));
  error.value = "";
}

function onFolderChange(e) {
  selectedFiles.value = filterAllowed(Array.from(e.target.files));
  error.value = "";
}


async function uploadFiles() {
  if (!selectedFiles.value.length) return;
  loading.value = true;
  error.value = "";
  uploadResult.value = "";

  const formData = new FormData();
  selectedFiles.value.forEach(file => {
    // 多文件字段名统一用 'files'
    formData.append('files', file, file.webkitRelativePath || file.name);
  });

  try {
    const response = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    if (response.ok) {
      uploadResult.value = data.message || "文件上传成功！";
      selectedFiles.value = [];
    } else {
      error.value = data.error || "上传失败";
    }
  } catch (e) {
    error.value = "网络错误";
  } finally {
    loading.value = false;
  }
}

async function reviewAllFiles() {
  try {
    loading.value = true;
    error.value = "";
    const resp = await fetch('/api/review-upload', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        academic_year: params.value.academic_year,
        province_code: params.value.province_code,
        unit_code: params.value.unit_code,
        major_code: params.value.major_code
      })
    });
    const data = await resp.json();
    if (resp.ok) {
      uploadResult.value = data.message;
      reviewDetails.value = data.details || [];
    } else {
      error.value = data.error || "处理失败";
      reviewDetails.value = [];
    }
  } catch (e) {
    error.value = "网络错误";
    reviewDetails.value = [];
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>


.stuLayout-container {
    margin-left:300px;
    padding: 24px;
    flex: 1;
}


@media screen and (min-width: 1440px) {
  .stuLayout-container {
    max-width: 1240px;
    margin: 0 auto 0 200px;
  }
}

@media screen and (max-width: 1024px) {
  .stuLayout-container {
    min-width: calc(100% - 200px);
  }
}

@media screen and (max-width: 768px) {
  .sidebar {
    width: 160px;
  }
  
  .stuLayout-container {
    margin-left: 160px;
    min-width: calc(100% - 160px);
  }
}

.logo {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 20px;
}

.menu {
  list-style: none;
  padding: 0;
}

.menu li {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  font-size: 100%;
  height: 40px;
  color: #2e2d2d;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  padding: 0 15px;
}

.menu li:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.menu li.highlight {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.25);
}

.menu i {
  margin-right: 10px;
  color: #40a9ff;
}

.params-input {
    margin: 20px 0;
    padding: 20px;
    border: 1px solid #eee;
    border-radius: 8px;
}

.input-group {
    margin: 10px 0;
    display: flex;
    align-items: center;
}

.input-group label {
    width: 100px;
    margin-right: 10px;
}

.input-group input {
    padding: 5px;
    border: 1px solid #ddd;
    border-radius: 4px;
    width: 200px;
}

.update-params-btn {
    margin-top: 10px;
    padding: 8px 16px;
    background-color: #40a9ff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.update-params-btn:hover {
    background-color: #1890ff;
}

.upload-buttons {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
}

.selected-files {
    margin: 15px 0;
    max-height: 200px;
    overflow-y: auto;
}

.selected-files ul {
    list-style: none;
    padding: 0;
}

.selected-files li {
    padding: 5px 0;
    font-size: 14px;
    color: #666;
}

.upload-btn {
    width: 100%;
    padding: 10px;
    margin-top: 10px;
    background-color: #40a9ff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.upload-btn:disabled {
    background-color: #ccc;
    cursor: not-allowed;
}

.review-details {
  margin: 20px 0;
}
.review-details table {
  border-collapse: collapse;
  width: 100%;
}
.review-details th, .review-details td {
  border: 1px solid #ccc;
  padding: 6px 10px;
  text-align: left;
}
</style>