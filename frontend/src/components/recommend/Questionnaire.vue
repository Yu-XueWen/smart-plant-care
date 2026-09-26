<template>
  <div class="questionnaire-wrapper">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="floating-leaf leaf-1">🌿</div>
      <div class="floating-leaf leaf-2">🍃</div>
      <div class="floating-leaf leaf-3">🌱</div>
      <div class="floating-leaf leaf-4">🌸</div>
    </div>

    <div class="questionnaire-container">
    <!-- 进度指示器 -->
    <div class="progress-indicator">
      <div class="progress-steps">
        <div 
          v-for="(step, index) in steps" 
          :key="index"
          class="progress-step"
          :class="{ 
            completed: currentStep > index, 
            active: currentStep === index 
          }"
        >
          <div class="step-circle">
            <el-icon v-if="currentStep > index" class="step-icon"><Check /></el-icon>
            <span v-else class="step-number">{{ index + 1 }}</span>
          </div>
          <div class="step-label">{{ step.label }}</div>
          <div v-if="index < steps.length - 1" class="step-connector" :class="{ completed: currentStep > index }"></div>
        </div>
      </div>
    </div>

    <!-- 多步骤表单 -->
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-position="top"
      class="questionnaire-form"
      @keyup.enter="handleNext"
    >
      <!-- 步骤1: 经验水平 -->
      <div v-show="currentStep === 0" class="form-step" key="step0">
        <div class="questionnaire-header">
          <div class="header-badge">第一步</div>
          <h2 class="header-title">您的养花经验如何?</h2>
          <p class="header-subtitle">了解您的经验水平,为您推荐合适难度的植物</p>
        </div>

        <el-radio-group v-model="form.experience_level" class="modern-radio-group">
          <el-radio-button value="beginner" class="modern-radio">
            <div class="radio-content">
              <div class="radio-visual">
                <span class="radio-emoji">🌱</span>
                <div class="radio-difficulty">
                  <el-tag size="small" type="success" effect="plain">简单</el-tag>
                </div>
              </div>
              <div class="radio-info">
                <div class="radio-title">新手入门</div>
                <div class="radio-desc">刚开始养花,需要简单易养的植物</div>
                <div class="radio-tags">
                  <el-tag size="small" round>绿萝</el-tag>
                  <el-tag size="small" round>吊兰</el-tag>
                  <el-tag size="small" round>仙人掌</el-tag>
                </div>
              </div>
            </div>
          </el-radio-button>
          <el-radio-button value="intermediate" class="modern-radio">
            <div class="radio-content">
              <div class="radio-visual">
                <span class="radio-emoji">🌿</span>
                <div class="radio-difficulty">
                  <el-tag size="small" type="warning" effect="plain">中等</el-tag>
                </div>
              </div>
              <div class="radio-info">
                <div class="radio-title">进阶爱好者</div>
                <div class="radio-desc">有一定经验,愿意尝试更多品种</div>
                <div class="radio-tags">
                  <el-tag size="small" round>月季</el-tag>
                  <el-tag size="small" round>茉莉</el-tag>
                  <el-tag size="small" round>蝴蝶兰</el-tag>
                </div>
              </div>
            </div>
          </el-radio-button>
          <el-radio-button value="advanced" class="modern-radio">
            <div class="radio-content">
              <div class="radio-visual">
                <span class="radio-emoji">🌳</span>
                <div class="radio-difficulty">
                  <el-tag size="small" type="danger" effect="plain">挑战</el-tag>
                </div>
              </div>
              <div class="radio-info">
                <div class="radio-title">资深玩家</div>
                <div class="radio-desc">经验丰富,可以养护高难度植物</div>
                <div class="radio-tags">
                  <el-tag size="small" round>食虫植物</el-tag>
                  <el-tag size="small" round>苔藓微景观</el-tag>
                  <el-tag size="small" round>原生 orchid</el-tag>
                </div>
              </div>
            </div>
          </el-radio-button>
        </el-radio-group>
      </div>

      <!-- 步骤2: 光照条件 -->
      <div v-show="currentStep === 1" class="form-step" key="step1">
        <div class="questionnaire-header">
          <div class="header-badge">第二步</div>
          <h2 class="header-title">您家中的光照条件如何?</h2>
          <p class="header-subtitle">光照是植物生长的关键,选择最符合您家环境的选项</p>
        </div>

        <div class="option-cards">
          <div
            v-for="option in lightOptions"
            :key="option.value"
            class="option-card"
            :class="{ active: form.light_condition === option.value }"
            @click="form.light_condition = option.value"
          >
            <div class="card-visual">
              <span class="card-emoji">{{ option.icon }}</span>
              <div class="card-light-meter">
                <div class="meter-bar">
                  <div 
                    class="meter-fill" 
                    :style="{ 
                      width: getLightMeterWidth(option.value),
                      background: getLightMeterColor(option.value)
                    }"
                  ></div>
                </div>
                <span class="meter-label">{{ getLightLabel(option.value) }}</span>
              </div>
            </div>
            <div class="card-content">
              <div class="card-title">{{ option.title }}</div>
              <div class="card-desc">{{ option.desc }}</div>
            </div>
            <div class="check-mark">
              <el-icon><Check /></el-icon>
            </div>
          </div>
        </div>
      </div>

      <!-- 步骤3: 空间大小 -->
      <div v-show="currentStep === 2" class="form-step" key="step2">
        <div class="questionnaire-header">
          <div class="header-badge">第三步</div>
          <h2 class="header-title">可用于摆放植物的空间大小?</h2>
          <p class="header-subtitle">根据您的空间大小,为您推荐合适尺寸的植物</p>
        </div>

        <div class="option-cards">
          <div
            v-for="option in spaceOptions"
            :key="option.value"
            class="option-card"
            :class="{ active: form.space_size === option.value }"
            @click="form.space_size = option.value"
          >
            <div class="card-visual">
              <span class="card-emoji">{{ option.icon }}</span>
              <div class="card-space-preview">
                <div class="preview-grid" :class="option.gridClass">
                  <div v-for="n in option.cellCount" :key="n" class="preview-cell"></div>
                </div>
              </div>
            </div>
            <div class="card-content">
              <div class="card-title">{{ option.title }}</div>
              <div class="card-desc">{{ option.desc }}</div>
            </div>
            <div class="check-mark">
              <el-icon><Check /></el-icon>
            </div>
          </div>
        </div>
      </div>

      <!-- 步骤4: 可用时间 -->
      <div v-show="currentStep === 3" class="form-step" key="step3">
        <div class="questionnaire-header">
          <div class="header-badge">第四步</div>
          <h2 class="header-title">每天能花多少时间照顾植物?</h2>
          <p class="header-subtitle">根据您的时间安排,推荐养护频率合适的植物</p>
        </div>

        <el-radio-group v-model="form.time_availability" class="modern-radio-group">
          <el-radio-button value="little" class="modern-radio">
            <div class="radio-content">
              <div class="radio-visual">
                <span class="radio-emoji">⚡</span>
                <div class="radio-time-indicator">
                  <div class="time-ring">
                    <svg viewBox="0 0 36 36">
                      <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#e8e8e8" stroke-width="3"/>
                      <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#52c41a" stroke-width="3" stroke-dasharray="25, 100"/>
                    </svg>
                  </div>
                  <span class="time-text">&lt; 5分钟</span>
                </div>
              </div>
              <div class="radio-info">
                <div class="radio-title">时间较少</div>
                <div class="radio-desc">希望植物容易打理,不需要频繁照顾</div>
                <div class="radio-suggestion">推荐: 多肉、仙人掌、虎皮兰</div>
              </div>
            </div>
          </el-radio-button>
          <el-radio-button value="moderate" class="modern-radio">
            <div class="radio-content">
              <div class="radio-visual">
                <span class="radio-emoji">🕐</span>
                <div class="radio-time-indicator">
                  <div class="time-ring">
                    <svg viewBox="0 0 36 36">
                      <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#e8e8e8" stroke-width="3"/>
                      <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#faad14" stroke-width="3" stroke-dasharray="50, 100"/>
                    </svg>
                  </div>
                  <span class="time-text">5-15分钟</span>
                </div>
              </div>
              <div class="radio-info">
                <div class="radio-title">时间适中</div>
                <div class="radio-desc">可以定期浇水和简单护理</div>
                <div class="radio-suggestion">推荐: 绿萝、吊兰、白掌</div>
              </div>
            </div>
          </el-radio-button>
          <el-radio-button value="much" class="modern-radio">
            <div class="radio-content">
              <div class="radio-visual">
                <span class="radio-emoji">💝</span>
                <div class="radio-time-indicator">
                  <div class="time-ring">
                    <svg viewBox="0 0 36 36">
                      <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#e8e8e8" stroke-width="3"/>
                      <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#722ed1" stroke-width="3" stroke-dasharray="85, 100"/>
                    </svg>
                  </div>
                  <span class="time-text">&gt; 15分钟</span>
                </div>
              </div>
              <div class="radio-info">
                <div class="radio-title">时间充足</div>
                <div class="radio-desc">愿意花时间精心照料植物</div>
                <div class="radio-suggestion">推荐: 兰花、蕨类、食虫植物</div>
              </div>
            </div>
          </el-radio-button>
        </el-radio-group>
      </div>

      <!-- 步骤5: 偏好标签 -->
      <div v-show="currentStep === 4" class="form-step" key="step4">
        <div class="questionnaire-header">
          <div class="header-badge">最后一步</div>
          <h2 class="header-title">您更喜欢什么类型的植物?</h2>
          <p class="header-subtitle">选择您感兴趣的植物类型,可以多选哦~</p>
        </div>

        <el-checkbox-group v-model="form.preferences" class="modern-checkbox-group">
          <div
            v-for="pref in preferenceOptions"
            :key="pref.value"
            class="preference-card"
            :class="{ selected: form.preferences.includes(pref.value) }"
            @click="togglePreference(pref.value)"
          >
            <div class="pref-visual">
              <span class="pref-emoji">{{ pref.icon }}</span>
              <div class="pref-count-badge" v-if="pref.count">
                {{ pref.count }}
              </div>
            </div>
            <div class="pref-content">
              <div class="pref-title">{{ pref.label }}</div>
              <div class="pref-desc">{{ pref.desc }}</div>
            </div>
            <div class="pref-check">
              <el-icon :size="20"><Check /></el-icon>
            </div>
          </div>
        </el-checkbox-group>
      </div>

      <!-- 导航按钮 -->
      <div class="navigation-buttons">
        <el-button
          v-if="currentStep > 0"
          size="large"
          class="nav-btn prev-btn"
          @click="handlePrev"
        >
          <el-icon><ArrowLeft /></el-icon>
          <span>上一步</span>
        </el-button>
        <div class="spacer" v-if="currentStep > 0"></div>
        <el-button
          v-if="currentStep < steps.length - 1"
          type="primary"
          size="large"
          class="nav-btn next-btn"
          @click="handleNext"
        >
          <span>下一步</span>
          <el-icon><ArrowRight /></el-icon>
        </el-button>
        <el-button
          v-else
          type="primary"
          size="large"
          :loading="loading"
          class="submit-btn"
          @click="handleSubmit"
        >
          <el-icon><MagicStick /></el-icon>
          <span>获取专属推荐</span>
        </el-button>
      </div>
    </el-form>
  </div>
</div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { Check, MagicStick, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import type { QuestionnaireAnswers } from '@/types/models'

const emit = defineEmits<{
  submit: [answers: QuestionnaireAnswers]
}>()

const formRef = ref<FormInstance>()
const loading = ref(false)
const currentStep = ref(0)

// 步骤定义
const steps = [
  { label: '经验水平', key: 'experience' },
  { label: '光照条件', key: 'light' },
  { label: '空间大小', key: 'space' },
  { label: '照顾时间', key: 'time' },
  { label: '植物偏好', key: 'prefs' }
]

const form = reactive<QuestionnaireAnswers>({
  experience_level: 'beginner',
  light_condition: 'medium',
  space_size: 'medium',
  time_availability: 'moderate',
  preferences: [],
  climate_zone: undefined
})

// 光照选项
const lightOptions = [
  { value: 'low', icon: '🌑', title: '弱光环境', desc: '离窗户较远,光线较弱' },
  { value: 'medium', icon: '⛅', title: '中等光照', desc: '靠近窗户,有散射光' },
  { value: 'high', icon: '☀️', title: '强光环境', desc: '阳光充足的位置' },
  { value: 'full_sun', icon: '🌞', title: '全日照', desc: '阳台或户外,直射阳光' }
]

// 空间选项
const spaceOptions = [
  { value: 'small', icon: '🪴', title: '小空间', desc: '桌面、窗台等小区域', gridClass: 'grid-small', cellCount: 4 },
  { value: 'medium', icon: '🏠', title: '中等空间', desc: '客厅一角、书架等', gridClass: 'grid-medium', cellCount: 9 },
  { value: 'large', icon: '🏡', title: '大空间', desc: '阳台、庭院等宽敞区域', gridClass: 'grid-large', cellCount: 16 }
]

// 偏好选项
const preferenceOptions = [
  { value: '开花', icon: '🌸', label: '开花植物', desc: '色彩斑斓,装点生活', count: 45 },
  { value: '观叶', icon: '🍃', label: '观叶植物', desc: '绿意盎然,清新自然', count: 38 },
  { value: '多肉', icon: '🌵', label: '多肉植物', desc: '小巧可爱,易于养护', count: 52 },
  { value: '空气净化', icon: '💨', label: '空气净化', desc: '改善室内空气质量', count: 28 },
  { value: '芳香', icon: '🌺', label: '芳香植物', desc: '花香四溢,舒缓身心', count: 22 },
  { value: '药用', icon: '💊', label: '药用植物', desc: '天然草药,养生保健', count: 15 },
  { value: '悬挂', icon: '🎋', label: '悬挂植物', desc: '立体绿化,节省空间', count: 18 },
  { value: '耐阴', icon: '🌑', label: '耐阴植物', desc: '无需阳光也能生长', count: 25 },
  { value: '耐旱', icon: '☀️', label: '耐旱植物', desc: '少浇水也能茁壮成长', count: 32 }
]

const rules: FormRules = {
  experience_level: [
    { required: true, message: '请选择您的养花经验', trigger: 'change' }
  ],
  light_condition: [
    { required: true, message: '请选择光照条件', trigger: 'change' }
  ],
  space_size: [
    { required: true, message: '请选择空间大小', trigger: 'change' }
  ],
  time_availability: [
    { required: true, message: '请选择可用时间', trigger: 'change' }
  ]
}

const handleNext = async () => {
  if (!formRef.value) return
  
  // 验证当前步骤
  const currentProp = steps[currentStep.value]?.key
  const validations: Record<string, string> = {
    experience: 'experience_level',
    light: 'light_condition',
    space: 'space_size',
    time: 'time_availability'
  }
  
  if (validations[currentProp || '']) {
    try {
      await formRef.value.validateField(validations[currentProp as string] || '')
      currentStep.value++
    } catch {
      // 验证失败,显示错误提示
    }
  } else {
    currentStep.value++
  }
}

const handlePrev = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate((valid) => {
    if (valid) {
      loading.value = true
      try {
        emit('submit', { ...form })
      } finally {
        loading.value = false
      }
    }
  })
}

const togglePreference = (value: string) => {
  const idx = form.preferences.indexOf(value)
  if (idx > -1) {
    form.preferences.splice(idx, 1)
  } else {
    form.preferences.push(value)
  }
}

// 光照计量条
const getLightMeterWidth = (value: string) => {
  const widths: Record<string, string> = {
    low: '25%',
    medium: '50%',
    high: '75%',
    full_sun: '100%'
  }
  return widths[value] || '50%'
}

const getLightMeterColor = (value: string) => {
  const colors: Record<string, string> = {
    low: '#597ef7',
    medium: '#fac858',
    high: '#ff7a45',
    full_sun: '#f5222d'
  }
  return colors[value] || '#fac858'
}

const getLightLabel = (value: string) => {
  const labels: Record<string, string> = {
    low: '低',
    medium: '中',
    high: '高',
    full_sun: '极高'
  }
  return labels[value] || '中'
}
</script>

<style scoped lang="scss">
// ========== 设计系统变量 ==========
$primary-green: #2d6a4f;
$primary-green-light: #40916c;
$primary-green-pale: #d8f3dc;
$accent-lime: #95d5b2;
$accent-warm: #ff8c69;
$accent-gold: #ffd166;
$text-primary: #1b4332;
$text-secondary: #52796f;
$text-muted: #74a892;
$bg-cream: #fefae0;
$bg-white: #ffffff;
$white: #ffffff;
$border-light: #b7e4c7;
$shadow-soft: 0 2px 12px rgba(45, 106, 79, 0.08);
$shadow-medium: 0 4px 20px rgba(45, 106, 79, 0.12);
$shadow-strong: 0 8px 30px rgba(45, 106, 79, 0.18);
$radius-sm: 8px;
$radius-md: 16px;
$radius-lg: 24px;
$radius-xl: 32px;
$transition-base: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
$transition-bounce: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);

// ========== 背景装饰 ==========
.questionnaire-wrapper {
  position: relative;
  min-height: 100vh;
  background: linear-gradient(165deg, #f0fdf4 0%, #fefce8 40%, #fdf2f8 100%);
  overflow: hidden;

  .bg-decoration {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;

    .floating-leaf {
      position: absolute;
      font-size: 48px;
      opacity: 0.12;
      animation: floatLeaf 20s ease-in-out infinite;

      &.leaf-1 {
        top: 10%;
        left: 5%;
        animation-delay: 0s;
        animation-duration: 22s;
      }
      &.leaf-2 {
        top: 30%;
        right: 8%;
        animation-delay: -5s;
        animation-duration: 18s;
      }
      &.leaf-3 {
        bottom: 20%;
        left: 10%;
        animation-delay: -10s;
        font-size: 36px;
      }
      &.leaf-4 {
        bottom: 40%;
        right: 5%;
        animation-delay: -15s;
        font-size: 42px;
      }
    }
  }
}

.questionnaire-container {
  position: relative;
  z-index: 1;
  max-width: 900px;
  margin: 0 auto;
  padding: 48px 24px 60px;
}

// ========== 进度指示器 ==========
.progress-indicator {
  margin-bottom: 48px;
  animation: fadeInDown 0.6s ease-out;

  .progress-steps {
    display: flex;
    align-items: flex-start;
    justify-content: center;
    gap: 0;
  }

  .progress-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
    flex: 1;
    max-width: 140px;

    .step-circle {
      width: 44px;
      height: 44px;
      border-radius: 50%;
      background: $bg-white;
      border: 2.5px solid $border-light;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: $transition-base;
      position: relative;
      z-index: 2;

      .step-icon {
        color: $primary-green;
        font-size: 20px;
      }

      .step-number {
        font-size: 16px;
        font-weight: 700;
        color: $text-muted;
        transition: $transition-base;
      }
    }

    .step-label {
      margin-top: 10px;
      font-size: 13px;
      font-weight: 500;
      color: $text-muted;
      transition: $transition-base;
      white-space: nowrap;
    }

    .step-connector {
      position: absolute;
      top: 22px;
      left: 55%;
      width: calc(100% - 10px);
      height: 2.5px;
      background: $border-light;
      z-index: 1;
      transition: $transition-base;

      &.completed {
        background: linear-gradient(90deg, $primary-green, $primary-green-light);
      }
    }

    &.active .step-circle {
      border-color: $primary-green;
      background: linear-gradient(135deg, $primary-green, $primary-green-light);
      box-shadow: 0 0 0 4px rgba(45, 106, 79, 0.15);
      transform: scale(1.1);

      .step-number {
        color: $white;
      }
    }

    &.completed .step-circle {
      border-color: $primary-green;
      background: $primary-green;

      .step-number {
        color: $white;
      }
    }

    &.active .step-label,
    &.completed .step-label {
      color: $primary-green;
      font-weight: 600;
    }
  }
}

// ========== 表单步骤 ==========
.questionnaire-form {
  animation: fadeInUp 0.5s ease-out;
}

.form-step {
  animation: stepFadeIn 0.4s ease-out;
}

@keyframes stepFadeIn {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

// ========== 头部样式 ==========
.questionnaire-header {
  text-align: center;
  margin-bottom: 40px;

  .header-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 16px;
    background: linear-gradient(135deg, $primary-green-pale, #bbf7d0);
    color: $primary-green;
    font-size: 13px;
    font-weight: 600;
    border-radius: 20px;
    margin-bottom: 16px;
    border: 1px solid rgba(45, 106, 79, 0.15);
  }

  .header-title {
    font-size: 30px;
    font-weight: 800;
    color: $text-primary;
    margin: 0 0 10px 0;
    line-height: 1.3;
    letter-spacing: -0.5px;
  }

  .header-subtitle {
    font-size: 15px;
    color: $text-secondary;
    margin: 0;
    line-height: 1.6;
    max-width: 480px;
    margin-inline: auto;
  }
}

// ========== 现代化单选组 ==========
.modern-radio-group {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 32px;

  :deep(.el-radio-button) {
    width: 100%;
    outline: none;

    .el-radio-button__inner {
      width: 100%;
      padding: 0;
      border: 2px solid $border-light;
      border-radius: $radius-md;
      background: $bg-white;
      transition: $transition-base;
      box-shadow: $shadow-soft;

      &:hover {
        border-color: $primary-green-light;
        transform: translateY(-3px);
        box-shadow: $shadow-medium;
      }
    }

    &.is-active .el-radio-button__inner {
      border-color: $primary-green;
      background: linear-gradient(135deg, rgba(45, 106, 79, 0.05), rgba(64, 145, 108, 0.08));
      box-shadow: 0 4px 20px rgba(45, 106, 79, 0.2), inset 0 0 0 2px $primary-green;
    }
  }
}

.radio-content {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;

  .radio-visual {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-shrink: 0;

    .radio-emoji {
      font-size: 42px;
      line-height: 1;
      transition: $transition-bounce;
    }

    .radio-difficulty {
      // 难度标签容器
    }
  }

  .radio-info {
    flex: 1;

    .radio-title {
      font-size: 18px;
      font-weight: 700;
      color: $text-primary;
      margin-bottom: 6px;
      transition: $transition-base;
    }

    .radio-desc {
      font-size: 14px;
      color: $text-secondary;
      line-height: 1.5;
      margin-bottom: 12px;
      transition: $transition-base;
    }

    .radio-tags,
    .radio-suggestion {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;

      :deep(.el-tag) {
        background: $primary-green-pale;
        border-color: transparent;
        color: $primary-green;
        font-size: 12px;
        padding: 2px 10px;
        height: 24px;
        line-height: 20px;
      }
    }

    .radio-suggestion {
      font-style: italic;
      opacity: 0.85;
    }
  }

  :deep(.is-active) & {
    .radio-title {
      color: $primary-green;
    }
    .radio-desc {
      color: $text-secondary;
    }
    .radio-emoji {
      transform: scale(1.15) rotate(-5deg);
    }
  }
}

// ========== 时间指示器 ==========
.radio-time-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;

  .time-ring {
    width: 52px;
    height: 52px;

    svg {
      width: 100%;
      height: 100%;
      transform: rotate(-90deg);

      path:last-child {
        transition: stroke-dasharray 0.5s ease;
      }
    }
  }

  .time-text {
    font-size: 11px;
    font-weight: 600;
    color: $text-secondary;
    white-space: nowrap;
  }
}

// ========== 选项卡片 ==========
.option-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 18px;
  margin-bottom: 32px;
}

.option-card {
  position: relative;
  padding: 28px 20px 24px;
  border: 2px solid $border-light;
  border-radius: $radius-md;
  background: $bg-white;
  cursor: pointer;
  transition: $transition-base;
  text-align: center;
  box-shadow: $shadow-soft;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, $primary-green, $accent-lime);
    opacity: 0;
    transition: $transition-base;
  }

  &:hover {
    border-color: $primary-green-light;
    transform: translateY(-5px);
    box-shadow: $shadow-medium;

    &::before {
      opacity: 1;
    }
  }

  &.active {
    border-color: $primary-green;
    background: linear-gradient(180deg, rgba(216, 243, 220, 0.4) 0%, $bg-white 100%);
    box-shadow: $shadow-strong;
    transform: translateY(-2px);

    &::before {
      opacity: 1;
      height: 4px;
    }
  }

  .card-visual {
    margin-bottom: 16px;

    .card-emoji {
      font-size: 48px;
      display: block;
      margin-bottom: 16px;
      transition: $transition-bounce;
    }

    .card-light-meter {
      .meter-bar {
        width: 100%;
        height: 6px;
        background: #f0f0f0;
        border-radius: 3px;
        overflow: hidden;
        margin-bottom: 6px;
      }

      .meter-fill {
        height: 100%;
        border-radius: 3px;
        transition: all 0.4s ease;
      }

      .meter-label {
        font-size: 12px;
        font-weight: 600;
        color: $text-secondary;
      }
    }

    .card-space-preview {
      .preview-grid {
        display: grid;
        gap: 4px;
        margin: 0 auto;
        width: fit-content;
        padding: 8px;
        background: #f8faf9;
        border-radius: $radius-sm;

        &.grid-small {
          grid-template-columns: repeat(2, 24px);
        }
        &.grid-medium {
          grid-template-columns: repeat(3, 24px);
        }
        &.grid-large {
          grid-template-columns: repeat(4, 24px);
        }

        .preview-cell {
          width: 24px;
          height: 24px;
          border-radius: 4px;
          background: linear-gradient(135deg, $primary-green-pale, $accent-lime);
          opacity: 0.6;
          transition: $transition-base;
        }
      }
    }
  }

  .card-content {
    .card-title {
      font-size: 17px;
      font-weight: 700;
      color: $text-primary;
      margin-bottom: 6px;
    }

    .card-desc {
      font-size: 13px;
      color: $text-secondary;
      line-height: 1.5;
    }
  }

  .check-mark {
    position: absolute;
    top: 14px;
    right: 14px;
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: linear-gradient(135deg, $primary-green, $primary-green-light);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transform: scale(0.5);
    transition: $transition-bounce;
    box-shadow: 0 2px 8px rgba(45, 106, 79, 0.3);

    .el-icon {
      font-size: 16px;
    }
  }

  &.active .check-mark {
    opacity: 1;
    transform: scale(1);
  }

  &.active .card-emoji {
    transform: scale(1.1);
  }
}

// ========== 偏好卡片 ==========
.modern-checkbox-group {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.preference-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px 20px;
  border: 2px solid $border-light;
  border-radius: $radius-md;
  background: $bg-white;
  cursor: pointer;
  transition: $transition-base;
  box-shadow: $shadow-soft;
  overflow: hidden;

  &::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(45, 106, 79, 0.05), rgba(149, 213, 178, 0.08));
    opacity: 0;
    transition: $transition-base;
  }

  &:hover {
    border-color: $primary-green-light;
    transform: translateY(-3px);
    box-shadow: $shadow-medium;

    &::after {
      opacity: 1;
    }
  }

  &.selected {
    border-color: $primary-green;
    background: $bg-white;
    box-shadow: 0 4px 16px rgba(45, 106, 79, 0.15);

    &::after {
      opacity: 1;
    }

    .pref-check {
      background: linear-gradient(135deg, $primary-green, $primary-green-light);
      color: white;
      border-color: $primary-green;
    }
  }

  .pref-visual {
    position: relative;
    flex-shrink: 0;

    .pref-emoji {
      font-size: 32px;
      line-height: 1;
      transition: $transition-bounce;
    }

    .pref-count-badge {
      position: absolute;
      top: -4px;
      right: -8px;
      min-width: 18px;
      height: 18px;
      padding: 0 5px;
      background: $accent-warm;
      color: white;
      font-size: 10px;
      font-weight: 700;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }

  .pref-content {
    flex: 1;
    position: relative;
    z-index: 1;

    .pref-title {
      font-size: 15px;
      font-weight: 600;
      color: $text-primary;
      margin-bottom: 2px;
      transition: $transition-base;
    }

    .pref-desc {
      font-size: 12px;
      color: $text-muted;
      line-height: 1.4;
    }
  }

  .pref-check {
    flex-shrink: 0;
    width: 22px;
    height: 22px;
    border: 2px solid $border-light;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: $transition-base;
    position: relative;
    z-index: 1;
  }

  &.selected .pref-emoji {
    transform: scale(1.15);
  }
}

// ========== 导航按钮 ==========
.navigation-buttons {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 40px;
  padding-top: 32px;
  border-top: 1px solid rgba(183, 228, 199, 0.4);

  .spacer {
    flex: 1;
  }
}

.nav-btn {
  flex: 0 0 auto;
  height: 52px;
  padding: 0 32px;
  font-size: 16px;
  font-weight: 600;
  border-radius: $radius-sm;
  transition: $transition-base;
  border: 2px solid $border-light;
  background: $bg-white;
  color: $text-secondary;

  &:hover {
    border-color: $primary-green-light;
    color: $primary-green;
    transform: translateY(-2px);
    box-shadow: $shadow-soft;
  }

  .el-icon {
    font-size: 18px;
  }

  &.prev-btn {
    .el-icon {
      margin-right: 4px;
    }
  }

  &.next-btn {
    background: linear-gradient(135deg, $primary-green, $primary-green-light);
    border-color: $primary-green;
    color: white;
    box-shadow: 0 4px 14px rgba(45, 106, 79, 0.25);

    &:hover {
      box-shadow: 0 6px 20px rgba(45, 106, 79, 0.35);
      transform: translateY(-3px);
    }

    .el-icon {
      margin-left: 4px;
    }
  }
}

.submit-btn {
  flex: 1;
  height: 56px;
  padding: 0 40px;
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, $primary-green 0%, $primary-green-light 50%, $accent-lime 100%);
  background-size: 200% 100%;
  border: none;
  border-radius: $radius-md;
  box-shadow: 0 6px 24px rgba(45, 106, 79, 0.3);
  transition: $transition-base;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.2), transparent);
    opacity: 0;
    transition: $transition-base;
  }

  &:hover {
    background-position: 100% 0;
    transform: translateY(-3px);
    box-shadow: 0 10px 32px rgba(45, 106, 79, 0.4);

    &::before {
      opacity: 1;
    }
  }

  &:active {
    transform: translateY(-1px);
  }

  .el-icon {
    font-size: 22px;
    margin-right: 8px;
  }
}

// ========== 动画 ==========
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-24px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(24px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes floatLeaf {
  0%, 100% {
    transform: translate(0, 0) rotate(0deg);
  }
  25% {
    transform: translate(15px, -20px) rotate(10deg);
  }
  50% {
    transform: translate(-10px, -35px) rotate(-5deg);
  }
  75% {
    transform: translate(20px, -15px) rotate(8deg);
  }
}

// ========== 响应式设计 ==========
@media (max-width: 768px) {
  .questionnaire-container {
    padding: 24px 16px 40px;
  }

  .progress-indicator {
    margin-bottom: 32px;

    .progress-steps {
      gap: 0;
    }

    .progress-step {
      .step-circle {
        width: 36px;
        height: 36px;

        .step-number {
          font-size: 14px;
        }
      }

      .step-label {
        font-size: 11px;
      }

      .step-connector {
        display: none;
      }
    }
  }

  .questionnaire-header {
    .header-badge {
      font-size: 12px;
      padding: 4px 12px;
    }

    .header-title {
      font-size: 24px;
    }

    .header-subtitle {
      font-size: 14px;
    }
  }

  .radio-content {
    flex-direction: column;
    text-align: center;
    padding: 20px 16px;

    .radio-visual {
      .radio-emoji {
        font-size: 36px;
      }
    }

    .radio-info {
      .radio-title {
        font-size: 16px;
      }

      .radio-tags {
        justify-content: center;
      }
    }
  }

  .option-cards {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .modern-checkbox-group {
    grid-template-columns: 1fr;
  }

  .navigation-buttons {
    flex-direction: column;

    .nav-btn {
      width: 100%;
    }

    .spacer {
      display: none;
    }
  }

  .submit-btn {
    width: 100%;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .questionnaire-container {
    max-width: 720px;
  }

  .option-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .modern-checkbox-group {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
