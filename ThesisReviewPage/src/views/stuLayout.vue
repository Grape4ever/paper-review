<template>
    <div>
        <aside class="sidebar">
        <div class="logo">毕业论文格式审核</div>
        
        <ul class="menu">
            <!-- <li 
            v-for="(value,index) in menu" 
            :key="index"
            :class="{'highlight' : isActive(value.url)}"
            @click="goToPage(value.url)"
            >
            <i class="menuvalue"></i> {{ value.name }}
            </li> -->
            <div>
            <h2>PDF文件上传</h2>
            <input
            ref="fileInput"
            type="file"
            @change="onFileChange"
            accept=".pdf,.doc,.docx,.zip"
            style="display: none"
            />
            <button @click="triggerFileSelect()">选择文件</button>
            <span v-if="selectedFile">{{ selectedFile.name }}</span>
            <br/><br/>
            <button :disabled="!selectedFile || loading" @click="uploadFile">
            {{ loading ? "正在上传..." : "上传并审核" }}
            </button>
            <div v-if="error" style="color: red; margin: 16px 0;">{{ error }}</div>
            <div v-if="downloadUrl" style="margin: 16px 0;">
            <a :href="downloadUrl" :download="downloadName">下载处理结果</a>
            </div>
        </div>
        </ul>
        </aside>
        <div class="stuLayout-container">
            <!-- 顶部提示栏 -->
            <div class="alert-bar">
            欢迎老师！
            
            </div>
        </div>
        <div>
            <h2>PDF 审核文件上传</h2>
            <input type="file" @change="onFileChange" accept=".pdf,.doc,.docx,.zip" />
            <br/><br/>
            <button :disabled="!selectedFile || loading" @click="uploadFile">
            {{ loading ? "正在上传..." : "上传并审核" }}
            </button>
            <div v-if="error" style="color: red; margin: 16px 0;">{{ error }}</div>
            <div v-if="downloadUrl" style="margin: 16px 0;">
            <a :href="downloadUrl" :download="downloadName">下载处理结果</a>
            </div>
        </div>
    </div>
    


</template>

<script setup>
import { ref } from "vue";

const fileInput = ref(null);
const selectedFile = ref(null);
const downloadUrl = ref("");
const downloadName = ref("");
const error = ref("");
const loading = ref(false);

function triggerFileSelect() {
  fileInput.value && fileInput.value.click();
}


function onFileChange(e) {
  selectedFile.value = e.target.files[0];
  downloadUrl.value = "";
  error.value = "";
}

async function uploadFile() {
  if (!selectedFile.value) return;
  loading.value = true;
  error.value = "";
  downloadUrl.value = "";
  downloadName.value = "";

  const formData = new FormData();
  formData.append("file", selectedFile.value);

  try {
    const response = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    if (response.ok) {
      error.value = "";
      alert(data.message || "上传成功！");
      selectedFile.value = null;
    } else {
      error.value = data.error || "上传失败";
    }
  } catch (e) {
    error.value = "网络错误";
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
</style> 