<template>
  <div class="admin-statistics">
    <!-- 快速统计 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-number">{{ borrowReturnRate }}%</div>
          <div class="stat-label">图书归还率</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-number">{{ topBooks.length }}</div>
          <div class="stat-label">热门图书</div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 热门图书 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <span>热门图书排行（前10名）</span>
        </div>
</template>
      
      <el-table :data="topBooks" stripe>
        <el-table-column type="index" label="排名" width="60" />
        <el-table-column prop="title" label="书名" />
        <el-table-column prop="author" label="作者" width="120" />
        <el-table-column prop="borrow_count" label="借阅次数" width="100" />
      </el-table>
    </el-card>
    
    <!-- 分类分布 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <span>图书分类分布</span>
        </div>
</template>
      
      <el-table :data="categoryDistribution" stripe>
        <el-table-column prop="category" label="分类" />
        <el-table-column prop="count" label="数量" width="100" />
      </el-table>
    </el-card>
    
    <!-- 逾期报告 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <span>逾期图书报告</span>
        </div>
</template>
      
      <el-table :data="overdueReport" stripe v-if="overdueReport.length > 0">
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="book_title" label="图书" />
        <el-table-column prop="due_time" label="应还日期" width="150" />
        <el-table-column prop="overdue_days" label="逾期天数" width="100">
          <template #default="{ row }">
            <el-tag type="danger">{{ row.overdue_days }}天</el-tag>
</template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="没有逾期图书" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  getTopBooksStatistics,
  getCategoryDistribution,
  getOverdueReport,
  getBorrowReturnRate
} from '@/api/admin'
import { ElMessage } from 'element-plus'

const topBooks = ref([])
const categoryDistribution = ref([])
const overdueReport = ref([])
const borrowReturnRate = ref(0)

const fetchStatistics = async () => {
  try {
    // 获取热门图书
    const booksRes = await getTopBooksStatistics({ limit: 10 })
    if (booksRes.code === 200) {
      topBooks.value = booksRes.data
    }
    
    // 获取分类分布
    const catRes = await getCategoryDistribution()
    if (catRes.code === 200) {
      categoryDistribution.value = catRes.data
    }
    
    // 获取逾期报告
    const overdueRes = await getOverdueReport()
    if (overdueRes.code === 200) {
      overdueReport.value = overdueRes.data
    }
    
    // 获取借还率
    const rateRes = await getBorrowReturnRate()
    if (rateRes.code === 200) {
      borrowReturnRate.value = rateRes.data.return_rate
    }
  } catch (error) {
    ElMessage.error('获取统计数据失败')
  }
}

onMounted(() => {
  fetchStatistics()
})
</script>

<style scoped>
.admin-statistics {
  padding-bottom: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #667eea;
  margin:  20px 0 10px;
}

.stat-label {
  color: #606266;
  font-size:  14px;
  margin-bottom: 20px;
}

.chart-card {
  margin-bottom: 20px;
}

.card-header {
  width: 100%;
}
</style>