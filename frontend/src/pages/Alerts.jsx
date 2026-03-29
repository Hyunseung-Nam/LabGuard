import AlertItem from '../components/AlertItem'

const ALERTS = [
  { id: 1, severity: 'alert', deviceName: '항온항습기 #1', message: '온도 임계치 초과 (37.2°C > 38.0°C 기준)', time: '오늘 02:14' },
  { id: 2, severity: 'alert', deviceName: '항온항습기 #1', message: '온도 임계치 초과 (38.9°C > 38.0°C 기준)', time: '어제 23:51' },
  { id: 3, severity: 'warning', deviceName: '진공 펌프 #2', message: '압력 이상 징후 감지 (3σ 초과)', time: '어제 18:30' },
  { id: 4, severity: 'offline', deviceName: '오실로스코프 #1', message: '장비 응답 없음 — 연결을 확인하세요', time: '3일 전 09:00' },
  { id: 5, severity: 'alert', deviceName: '항온항습기 #3', message: '온도 임계치 초과 (40.1°C > 38.0°C 기준)', time: '5일 전 14:22' },
]

export default function Alerts() {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-xl font-semibold text-gray-900 mb-1">알림 내역</h1>
      <p className="text-sm text-gray-400 mb-8">감지된 모든 이상 이벤트 기록입니다.</p>

      <div className="flex flex-col gap-2">
        {ALERTS.map((a) => (
          <AlertItem key={a.id} {...a} />
        ))}
      </div>

      {ALERTS.length === 0 && (
        <div className="text-center py-20 text-gray-300 text-sm">알림 내역이 없습니다.</div>
      )}
    </div>
  )
}
