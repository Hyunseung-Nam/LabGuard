const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'

/**
 * 목적: 공통 fetch 래퍼. 모든 API 호출은 이 함수를 통해 처리합니다.
 * Args: endpoint (string), options (RequestInit)
 * Returns: JSON 파싱된 응답 데이터.
 * Raises: Error - 네트워크 오류 또는 4xx/5xx 응답 시.
 */
async function request(endpoint, options = {}) {
  const res = await fetch(`${BASE_URL}${endpoint}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    throw new Error(`API 오류: ${res.status} ${res.statusText}`)
  }
  if (res.status === 204) return null
  return res.json()
}

export const api = {
  // 장비
  getDevices: () => request('/devices'),
  getDevice: (id) => request(`/devices/${id}`),
  createDevice: (data) => request('/devices', { method: 'POST', body: JSON.stringify(data) }),
  deleteDevice: (id) => request(`/devices/${id}`, { method: 'DELETE' }),

  // 측정값
  getMeasurements: (deviceId, params = {}) => {
    const qs = new URLSearchParams({ device_id: deviceId, ...params }).toString()
    return request(`/measurements?${qs}`)
  },

  // 알림
  getAlerts: (deviceId) => {
    const qs = deviceId ? `?device_id=${deviceId}` : ''
    return request(`/alerts${qs}`)
  },
  acknowledgeAlert: (id) => request(`/alerts/${id}/acknowledge`, { method: 'POST' }),

  // 대시보드
  getDashboardSummary: () => request('/dashboard/summary'),
}
