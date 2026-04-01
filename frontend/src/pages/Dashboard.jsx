import { useEffect, useState } from 'react'
import DeviceCard from '../components/DeviceCard'
import AlertItem from '../components/AlertItem'
import { api } from '../api/client'

function deriveStatus(deviceId, alerts) {
  const latest = alerts.filter((a) => a.device_id === deviceId).at(0)
  if (!latest) return 'normal'
  const age = Date.now() - new Date(latest.time).getTime()
  if (age > 60_000) return 'normal'
  return latest.severity.toLowerCase()
}

function formatTime(iso) {
  const d = new Date(iso)
  const now = new Date()
  const diffMs = now - d
  const diffMin = Math.floor(diffMs / 60000)
  if (diffMin < 1) return '방금 전'
  if (diffMin < 60) return `${diffMin}분 전`
  const diffH = Math.floor(diffMin / 60)
  if (diffH < 24) return `${diffH}시간 전`
  return `${Math.floor(diffH / 24)}일 전`
}

export default function Dashboard() {
  const [summary, setSummary] = useState({ total_devices: 0, alert_count: 0, alert_device_count: 0 })
  const [devices, setDevices] = useState([])
  const [alerts, setAlerts] = useState([])
  const [latestMap, setLatestMap] = useState({})  // device_id → 최신 측정값
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const [s, d, a] = await Promise.all([
          api.getDashboardSummary(),
          api.getDevices(),
          api.getAlerts(),
        ])
        setSummary(s)
        setDevices(d)
        setAlerts(a.slice(0, 20))

        // 각 장비의 최신 측정값 1건씩 병렬 조회
        const entries = await Promise.all(
          d.map(async (dev) => {
            try {
              const meas = await api.getMeasurements(dev.id, { limit: 1 })
              return [dev.id, meas[0] ?? null]
            } catch {
              return [dev.id, null]
            }
          })
        )
        setLatestMap(Object.fromEntries(entries))
      } catch (e) {
        console.error('대시보드 로드 실패:', e)
      } finally {
        setLoading(false)
      }
    }
    load()

    // 10초마다 갱신
    const timer = setInterval(load, 10000)
    return () => clearInterval(timer)
  }, [])

  const stats = [
    { label: '전체 장비', value: summary.total_devices },
    { label: '이상 장비', value: summary.alert_device_count },
  ]

  if (loading) {
    return <div className="text-sm text-gray-400 mt-20 text-center">불러오는 중...</div>
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-xl font-semibold text-gray-900 mb-1">대시보드</h1>
      <p className="text-sm text-gray-400 mb-8">장비 전체 현황을 한눈에 확인합니다.</p>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {stats.map((s) => (
          <div key={s.label} className="bg-white border border-gray-100 rounded-xl p-4 text-center">
            <p className="text-2xl font-semibold text-gray-900">{s.value}</p>
            <p className="text-xs text-gray-400 mt-1">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Devices */}
      <h2 className="text-sm font-medium text-gray-500 mb-3">장비 상태</h2>
      {devices.length === 0 ? (
        <p className="text-sm text-gray-300 mb-10">등록된 장비가 없습니다.</p>
      ) : (
        <div className="grid grid-cols-2 gap-4 mb-10">
          {devices.map((d) => {
            const latest = latestMap[d.id]
            const value = latest
              ? `${latest.raw_value?.toFixed(2)} ${latest.unit ?? ''}`
              : '—'
            const metric = latest?.metric ?? '—'
            return (
              <DeviceCard
                key={d.id}
                name={d.name}
                location={d.location}
                metric={metric}
                value={value}
                status={deriveStatus(d.id, alerts)}
              />
            )
          })}
        </div>
      )}

      {/* Recent Alerts */}
      <h2 className="text-sm font-medium text-gray-500 mb-3">최근 알림</h2>
      {alerts.length === 0 ? (
        <p className="text-sm text-gray-300">알림 내역이 없습니다.</p>
      ) : (
        <div className="flex flex-col gap-2">
          {alerts.map((a) => (
            <AlertItem
              key={a.id}
              severity={a.severity.toLowerCase()}
              deviceName={devices.find((d) => d.id === a.device_id)?.name ?? a.device_id}
              message={a.message}
              time={formatTime(a.time)}
            />
          ))}
        </div>
      )}
    </div>
  )
}
