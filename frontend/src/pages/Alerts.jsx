import { useEffect, useState } from 'react'
import AlertItem from '../components/AlertItem'
import { api } from '../api/client'

function formatTime(iso) {
  const d = new Date(iso)
  return d.toLocaleString('ko-KR', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

export default function Alerts() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getAlerts()
      .then(setAlerts)
      .catch((e) => console.error('알림 로드 실패:', e))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className="text-sm text-gray-400 mt-20 text-center">불러오는 중...</div>
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-xl font-semibold text-gray-900 mb-1">알림 내역</h1>
      <p className="text-sm text-gray-400 mb-8">감지된 모든 이상 이벤트 기록입니다.</p>

      {alerts.length === 0 ? (
        <div className="text-center py-20 text-gray-300 text-sm">알림 내역이 없습니다.</div>
      ) : (
        <div className="flex flex-col gap-2">
          {alerts.map((a) => (
            <AlertItem
              key={a.id}
              severity={a.severity.toLowerCase()}
              deviceName={a.device_id}
              message={a.message}
              time={formatTime(a.time)}
            />
          ))}
        </div>
      )}
    </div>
  )
}
