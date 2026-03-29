import DeviceCard from '../components/DeviceCard'
import AlertItem from '../components/AlertItem'

// 더미 데이터 — 실제 API 연동 전 UI 확인용
const DEVICES = [
  { id: 1, name: '항온항습기 #1', location: 'B동 512호', metric: 'Temperature', value: '37.2°C', status: 'alert' },
  { id: 2, name: '진공 펌프 #2', location: 'B동 512호', metric: 'Pressure', value: '0.3 mbar', status: 'normal' },
  { id: 3, name: '항온항습기 #3', location: 'A동 308호', metric: 'Temperature', value: '25.1°C', status: 'normal' },
  { id: 4, name: '오실로스코프 #1', location: 'A동 308호', metric: 'Voltage', value: '—', status: 'offline' },
]

const RECENT_ALERTS = [
  { id: 1, severity: 'alert', deviceName: '항온항습기 #1', message: '온도 임계치 초과 (37.2°C > 38.0°C 기준)', time: '02:14' },
  { id: 2, severity: 'warning', deviceName: '진공 펌프 #2', message: '압력 이상 징후 감지 (3σ 초과)', time: '어제' },
  { id: 3, severity: 'offline', deviceName: '오실로스코프 #1', message: '장비 응답 없음', time: '3일 전' },
]

const stats = [
  { label: '전체 장비', value: '4' },
  { label: '정상', value: '2' },
  { label: '경고/알림', value: '1' },
  { label: '오프라인', value: '1' },
]

export default function Dashboard() {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-xl font-semibold text-gray-900 mb-1">대시보드</h1>
      <p className="text-sm text-gray-400 mb-8">장비 전체 현황을 한눈에 확인합니다.</p>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        {stats.map((s) => (
          <div key={s.label} className="bg-white border border-gray-100 rounded-xl p-4 text-center">
            <p className="text-2xl font-semibold text-gray-900">{s.value}</p>
            <p className="text-xs text-gray-400 mt-1">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Devices */}
      <h2 className="text-sm font-medium text-gray-500 mb-3">장비 상태</h2>
      <div className="grid grid-cols-2 gap-4 mb-10">
        {DEVICES.map((d) => (
          <DeviceCard key={d.id} {...d} />
        ))}
      </div>

      {/* Recent Alerts */}
      <h2 className="text-sm font-medium text-gray-500 mb-3">최근 알림</h2>
      <div className="flex flex-col gap-2">
        {RECENT_ALERTS.map((a) => (
          <AlertItem key={a.id} {...a} />
        ))}
      </div>
    </div>
  )
}
