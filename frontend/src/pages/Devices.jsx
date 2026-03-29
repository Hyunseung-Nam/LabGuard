import { useEffect, useState } from 'react'
import { Cpu, Add } from 'iconsax-react'
import { api } from '../api/client'

const statusLabel = {
  normal: { text: '정상', className: 'text-emerald-600 bg-emerald-50' },
  warning: { text: '경고', className: 'text-yellow-600 bg-yellow-50' },
  alert: { text: '알림', className: 'text-red-600 bg-red-50' },
  offline: { text: '오프라인', className: 'text-gray-500 bg-gray-100' },
}

export default function Devices() {
  const [devices, setDevices] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getDevices()
      .then(setDevices)
      .catch((e) => console.error('장비 목록 로드 실패:', e))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className="text-sm text-gray-400 mt-20 text-center">불러오는 중...</div>
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-xl font-semibold text-gray-900 mb-1">장비 관리</h1>
          <p className="text-sm text-gray-400">등록된 실험 장비 목록입니다.</p>
        </div>
        <button className="flex items-center gap-2 bg-blue-500 hover:bg-blue-600 text-white text-sm px-4 py-2 rounded-lg transition-colors">
          <Add size={16} />
          장비 추가
        </button>
      </div>

      <div className="bg-white border border-gray-100 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100 text-gray-400 text-left">
              <th className="px-5 py-3 font-medium">장비명</th>
              <th className="px-5 py-3 font-medium">프로토콜</th>
              <th className="px-5 py-3 font-medium">위치</th>
              <th className="px-5 py-3 font-medium">상태</th>
            </tr>
          </thead>
          <tbody>
            {devices.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-5 py-10 text-center text-gray-300 text-sm">
                  등록된 장비가 없습니다.
                </td>
              </tr>
            ) : (
              devices.map((d) => {
                const s = statusLabel['normal']
                return (
                  <tr key={d.id} className="border-b border-gray-50 last:border-0 hover:bg-gray-50 transition-colors">
                    <td className="px-5 py-3.5">
                      <span className="flex items-center gap-2 text-gray-800 font-medium">
                        <Cpu size={15} color="#9ca3af" />
                        {d.name}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-gray-500 font-mono text-xs">{d.protocol}</td>
                    <td className="px-5 py-3.5 text-gray-500">{d.location ?? '—'}</td>
                    <td className="px-5 py-3.5">
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${s.className}`}>
                        {s.text}
                      </span>
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
