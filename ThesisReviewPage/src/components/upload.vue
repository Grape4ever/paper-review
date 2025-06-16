<template>
  <div style="max-width: 400px; margin: 40px auto; border: 1px solid #eee; border-radius: 8px; padding: 24px;">
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
</template>

<script setup>
import { ref } from "vue";

const selectedFile = ref(null);
const downloadUrl = ref("");
const downloadName = ref("");
const error = ref("");
const loading = ref(false);

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
    const response = await fetch("../../api/upload", {
      method: "POST",
      body: formData,
    });

    // 检查是否是错误返回（JSON），否则是文件
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
      const data = await response.json();
      error.value = data.error || "上传失败";
    } else if (response.ok) {
      // 从响应头提取返回文件名
      const disposition = response.headers.get("Content-Disposition");
      let filename = "result.pdf";
      if (disposition) {
        const match = disposition.match(/filename="?([^"]+)"?/);
        if (match) filename = decodeURIComponent(match[1]);
      }
      const blob = await response.blob();
      downloadUrl.value = URL.createObjectURL(blob);
      downloadName.value = filename;
    } else {
      error.value = "上传失败";
    }
  } catch (e) {
    error.value = "网络错误";
  } finally {
    loading.value = false;
  }
}
</script>