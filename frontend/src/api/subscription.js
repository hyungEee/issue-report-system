const API_BASE_URL = 'http://localhost:8000'

export async function putSubscription(payload) {
  const response = await fetch(`${API_BASE_URL}/settings`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => null)
    const message = errorData?.detail || '구독 처리 중 오류가 발생했습니다.'
    throw new Error(message)
  }
}
