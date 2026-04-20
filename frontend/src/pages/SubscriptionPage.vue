<template>
  <div class="subscription-page">
    <div class="card">
      <h1>뉴스 구독 설정</h1>
      <p class="description">
        이메일과 관심 지역, 관심 카테고리를 선택한 뒤 구독 버튼을 눌러주세요.
      </p>

      <form @submit.prevent="submitSubscription">
        <div class="form-group">
          <label for="email">이메일</label>
          <input
            id="email"
            v-model.trim="form.email"
            type="email"
            placeholder="example@email.com"
            required
          />
        </div>

        <div class="form-group">
          <div class="group-title">관심 국가</div>
          <p class="helper-text">여러 개 선택할 수 있습니다.</p>
          <div class="checkbox-grid">
            <label
              v-for="region in regionOptions"
              :key="region.value"
              class="checkbox-item"
            >
              <input
                v-model="form.regions"
                type="checkbox"
                :value="region.value"
              />
              <span>{{ region.label }}</span>
            </label>
          </div>
        </div>

        <div class="form-group">
          <div class="group-title">관심 카테고리</div>
          <p class="helper-text">여러 개 선택할 수 있습니다.</p>
          <div class="checkbox-grid">
            <label
              v-for="category in categoryOptions"
              :key="category.value"
              class="checkbox-item"
            >
              <input
                v-model="form.categories"
                type="checkbox"
                :value="category.value"
              />
              <span>{{ category.label }}</span>
            </label>
          </div>
        </div>

        <div class="button-row">
          <button type="submit" :disabled="loading">
            {{ loading ? '구독 중...' : '구독' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { putSubscription } from '../api/subscription.js'

const loading = ref(false)

const regionOptions = [
  { label: '한국', value: 'korea' },
  { label: '북미', value: 'north_america' },
  { label: '아시아', value: 'asia' },
  { label: '유럽', value: 'europe' },
  { label: '중동/아프리카', value: 'middle_east_africa' },
]

const categoryOptions = [
  { label: '국제', value: 'world' },
  { label: '정치/사회', value: 'nation' },
  { label: '비즈니스', value: 'business' },
  { label: '기술', value: 'technology' },
  { label: '엔터테인먼트', value: 'entertainment' },
  { label: '스포츠', value: 'sports' },
  { label: '과학', value: 'science' },
]

const form = reactive({
  email: '',
  regions: [],
  categories: [],
})

async function submitSubscription() {
  loading.value = true
  try {
    await putSubscription({
      email: form.email,
      alert_enabled: true,
      regions: form.regions.length > 0 ? [...form.regions] : null,
      categories: form.categories.length > 0 ? [...form.categories] : null,
    })
    alert('구독이 완료되었습니다.')
    form.email = ''
    form.regions = []
    form.categories = []
  } catch (error) {
    alert(error.message || '구독 처리 중 오류가 발생했습니다.')
  } finally {
    loading.value = false
  }
}
</script>

<style src="./SubscriptionPage.css" />
