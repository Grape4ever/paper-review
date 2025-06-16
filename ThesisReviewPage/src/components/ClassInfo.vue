<template>
    <stuLayout>
        
            <button class="create-class-btn" @click="showCreateClassDialog">
                <span class="material-icons">add</span>
                加入班级
            </button>


        
            <table class="class-table">
                <thead>
                    <tr>
                        <th>班级名称</th>
                        <th>负责教师</th>
                        <th>学生人数</th>
                        <th style="text-align: center;">操作</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="classInfo in classes" :key="classInfo.class_id">
                        <td>{{ classInfo.class_name }}</td>
                        <td>{{ classInfo.teacher_name }}</td>
                        <td>{{ classInfo.student_count }}</td>
                        <td style="text-align: center;">
                            <button 
                                class="action-btn primary-btn" 
                                
                            >
                                查看
                            </button>
                            <button 
                                class="delete-btn primary-btn" 
                                @click="handleQuitClass(classInfo.class_id)"
                            >
                                退出
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
       

        <!-- 加入班级对话框 -->
        <div class="dialog-overlay" v-if="showJoinDialog">
            <div class="dialog-content">
                <div class="dialog-header">
                    <h2>加入班级</h2>
                    <span class="material-icons close-btn" @click="hideJoinDialog">close</span>
                </div>
                <form @submit.prevent="handleJoinClass">
                    <div class="form-group">
                        <label for="classCode">班级邀请码</label>
                        <input 
                            type="text" 
                            id="classCode" 
                            v-model="classCode" 
                            required 
                            placeholder="请输入班级邀请码"
                        >
                    </div>
                    <div class="dialog-footer">
                        <button type="button" class="delete-btn" @click="hideJoinDialog">取消</button>
                        <button type="submit" class="submit-btn">加入班级</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- 班级成员对话框 -->
        <div class="dialog-overlay" v-if="showMembersDialog">
            <div class="dialog-content" style="width: 600px;">
                <div class="dialog-header">
                    <div style="display: flex; align-items: center;">
                        <span 
                            class="material-icons back-btn" 
                            @click="hideMembersDialog"
                            style="margin-right: 12px; cursor: pointer;"
                        >
                            arrow_back
                        </span>
                        <h2>班级成员列表</h2>
                    </div>
                    <span class="material-icons close-btn" @click="hideMembersDialog">close</span>
                </div>
                <table class="class-table">
                    <thead>
                        <tr>
                            <th>学号</th>
                            <th>姓名</th>
                            <th>出勤次数</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="member in classMembers" :key="member.id">
                            <td>{{ member.student_id }}</td>
                            <td>{{ member.name }}</td>
                            <td>{{ member.attendance_count }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </stuLayout>
</template>

<script>
import stuLayout from '../views/stuLayout.vue';
// import { useAuth } from '../../../../../../../../../../vuecli/signin_system/src/composables/useAuth.js';
import { ref, onMounted } from 'vue';
// import { loadStudentClasses,
//         joinClass,
//         quitClass
//         } from '../../../../../../../../../../vuecli/signin_system/src/api/StuClassInfo.js';

export default {
    name:'ClassInfo',
    components:{
        stuLayout
    },
    setup() {
    const {isLoggedIn, username,checkLoginStatu,logouts} = useAuth();
    const classes = ref([]);
        const showJoinDialog = ref(false);
        const showMembersDialog = ref(false);
        const classCode = ref('');
        const classMembers = ref([]);

        const loadClasses = async () => {
            try {
                const studentId = localStorage.getItem('username');
                classes.value = await loadStudentClasses(studentId);
            } catch (error) {
                alert('加载班级列表失败');
            }
        };

        const showCreateClassDialog = () => {
            showJoinDialog.value = true;
        };

        const hideJoinDialog = () => {
            showJoinDialog.value = false;
            classCode.value = '';
        };

        const handleJoinClass = async () => {
            try {
                const studentId = localStorage.getItem('username');
                await joinClass(studentId, classCode.value);
                alert('加入班级成功！');
                hideJoinDialog();
                await loadClasses();
            } catch (error) {
                alert('加入班级失败');
            }
        };

        const handleQuitClass = async (classId) => {
            try {
                const studentId = localStorage.getItem('username');
                const result = await quitClass(studentId, classId);
                alert(result.message);
                await loadClasses();
            } catch (error) {
                alert('退出班级失败');
            }
        };

        const hideMembersDialog = () => {
            showMembersDialog.value = false;
        };

        onMounted(() => {
            loadClasses();
        });
    return {
        isLoggedIn,
        username,
        checkLoginStatu,
        logouts,
        classes,
        showJoinDialog,
        showMembersDialog,
        classCode,
        classMembers,
        showCreateClassDialog,
        hideJoinDialog,
        handleJoinClass,
        handleQuitClass,
        hideMembersDialog
    }
  },
}
</script>

<style scoped>
.create-class-btn {

    color: white;
    border: none;
    padding: 0 20px;
    height: 36px;
    border-radius: 36px;
    font-size: 14px;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    transition: background-color 0.2s;
}
.class-table {
            width: 100%;
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
            border-collapse: collapse;
            margin-top: 20px;
        }

        .class-table th,
        .class-table td {
            padding: 16px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }

        .class-table th {
            color: #5f6368;
            font-weight: 500;
            font-size: 14px;
            background: #f8f9fa;
        }

        .class-table td {
            color: #202124;
            font-size: 14px;
        }

        .class-table tr:hover {
            background-color: #f8f9fa;
        }
        .dialog-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }

        .dialog-content {
            background: white;
            border-radius: 8px;
            width: 400px;
            max-width: 90%;
            padding: 24px;
        }

        .dialog-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .dialog-header h2 {
            margin: 0;
            font-size: 20px;
            color: #202124;
        }
        .dialog-footer {
            display: flex;
            justify-content: flex-end;
            gap: 12px;
        }

</style>