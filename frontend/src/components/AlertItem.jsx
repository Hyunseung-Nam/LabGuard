import { Warning2, InfoCircle, CloseCircle } from 'iconsax-react'

/**
 * 알림 내역 리스트의 단일 항목 컴포넌트.
 *
 * @param {Object} props
 * @param {'warning'|'alert'|'offline'} props.severity - 심각도
 * @param {string} props.deviceName - 장비 이름
 * @param {string} props.message - 알림 메시지
 * @param {string} props.time - 발생 시각
 */
export default function AlertItem({ severity, deviceName, message, time }) {
  const config = {
    alert: { icon: CloseCircle, color: '#ef4444', bg: 'bg-red-50', border: 'border-red-100' },
    warning: { icon: Warning2, color: '#f59e0b', bg: 'bg-yellow-50', border: 'border-yellow-100' },
    offline: { icon: InfoCircle, color: '#9ca3af', bg: 'bg-gray-50', border: 'border-gray-100' },
  }

  const cfg = config[severity] ?? config.offline
  const Icon = cfg.icon

  return (
    <div className={`flex items-start gap-3 p-4 rounded-lg border ${cfg.bg} ${cfg.border}`}>
      <Icon size={18} color={cfg.color} variant="Bold" className="mt-0.5 shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-800">{deviceName}</p>
        <p className="text-sm text-gray-500 mt-0.5">{message}</p>
      </div>
      <span className="text-xs text-gray-400 shrink-0">{time}</span>
    </div>
  )
}
