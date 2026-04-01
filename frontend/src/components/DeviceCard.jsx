import { Cpu, ArrowUp } from 'iconsax-react'

/**
 * 개별 장비 상태를 요약해서 보여주는 카드 컴포넌트.
 *
 * @param {Object} props
 * @param {string} props.name - 장비 이름
 * @param {string} props.location - 장비 위치
 * @param {string} props.metric - 측정 항목 (예: 'Temperature')
 * @param {string} props.value - 현재 측정값 (예: '37.2°C')
 * @param {'normal'|'warning'|'alert'|'offline'} props.status - 장비 상태
 */
export default function DeviceCard({ name, location, metric, value, status }) {
  const statusConfig = {
    normal: { dot: 'bg-emerald-400', text: '정상', badge: 'text-emerald-600 bg-emerald-50' },
    high: { dot: 'bg-red-400 animate-pulse', text: '상한 초과', badge: 'text-red-600 bg-red-50' },
    low: { dot: 'bg-blue-400 animate-pulse', text: '하한 미달', badge: 'text-blue-600 bg-blue-50' },
    offline: { dot: 'bg-gray-300', text: '오프라인', badge: 'text-gray-500 bg-gray-100' },
  }

  const cfg = statusConfig[status] ?? statusConfig.offline

  return (
    <div className="bg-white border border-gray-100 rounded-xl p-5 flex flex-col gap-4 hover:shadow-sm transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <Cpu size={16} color="#6b7280" />
          <span className="text-sm font-medium text-gray-800">{name}</span>
        </div>
        <span className={`flex items-center gap-1.5 text-xs px-2 py-0.5 rounded-full font-medium ${cfg.badge}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
          {cfg.text}
        </span>
      </div>

      {/* Value */}
      <div>
        <p className="text-2xl font-semibold text-gray-900">{value}</p>
        <p className="text-xs text-gray-400 mt-0.5">{metric}</p>
      </div>

      {/* Footer */}
      <p className="text-xs text-gray-400">{location}</p>
    </div>
  )
}
