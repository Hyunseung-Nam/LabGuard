import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Cpu } from 'iconsax-react'
import { api } from '../api/client'

const statusLabel = {
  normal: { text: '정상', className: 'text-emerald-600 bg-emerald-50' },
  warning: { text: '경고', className: 'text-yellow-600 bg-yellow-50' },
  alert: { text: '알림', className: 'text-red-600 bg-red-50' },
  offline: { text: '오프라인', className: 'text-gray-500 bg-gray-100' },
}

const PROTOCOLS = ['serial', 'tcp', 'visa', 'modbus', 'simulated']

const EMPTY_FORM = { name: '', location: '', protocol: 'serial' }

export default function Devices() {
  const navigate = useNavigate()
  const [devices, setDevices] = useState([])
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const [submitting, setSubmitting] = useState(false)

  function loadData() {
    return Promise.all([api.getDevices(), api.getAlerts()])
      .then(([devs, alts]) => { setDevices(devs); setAlerts(alts) })
      .catch((e) => console.error('장비 목록 로드 실패:', e))
  }

  useEffect(() => {
    loadData().finally(() => setLoading(false))

    // 10초마다 갱신
    const timer = setInterval(loadData, 10000)
    return () => clearInterval(timer)
  }, [])

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    try {
      await api.createDevice({
        name: form.name.trim(),
        location: form.location.trim() || null,
        protocol: form.protocol,
        config: {},
        threshold: {},
      })
      setShowModal(false)
      setForm(EMPTY_FORM)
      await loadData()
    } catch (err) {
      console.error('장비 등록 실패:', err)
      alert('장비 등록에 실패했습니다.')
    } finally {
      setSubmitting(false)
    }
  }

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
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 bg-blue-500 hover:bg-blue-600 text-white text-sm px-4 py-2 rounded-lg transition-colors"
        >
          + 장비 추가
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
                const hasAlert = alerts.some((a) => a.device_id === d.id && !a.notified)
                const s = statusLabel[hasAlert ? 'alert' : 'normal']
                return (
                  <tr
                    key={d.id}
                    onClick={() => navigate(`/devices/${d.id}`)}
                    className="border-b border-gray-50 last:border-0 hover:bg-gray-50 transition-colors cursor-pointer"
                  >
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

      {/* 장비 추가 모달 */}
      {showModal && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
            <h2 className="text-base font-semibold text-gray-900 mb-5">장비 추가</h2>
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              <div>
                <label className="text-xs text-gray-500 mb-1 block">장비명 *</label>
                <input
                  type="text"
                  required
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  placeholder="예: 온도계-A"
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
              </div>
              <div>
                <label className="text-xs text-gray-500 mb-1 block">위치</label>
                <input
                  type="text"
                  value={form.location}
                  onChange={(e) => setForm({ ...form, location: e.target.value })}
                  placeholder="예: 실험실 1"
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
              </div>
              <div>
                <label className="text-xs text-gray-500 mb-1 block">프로토콜 *</label>
                <select
                  value={form.protocol}
                  onChange={(e) => setForm({ ...form, protocol: e.target.value })}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                >
                  {PROTOCOLS.map((p) => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
              </div>
              <div className="flex gap-2 mt-2">
                <button
                  type="button"
                  onClick={() => { setShowModal(false); setForm(EMPTY_FORM) }}
                  className="flex-1 border border-gray-200 text-gray-500 text-sm py-2 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  취소
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 text-white text-sm py-2 rounded-lg transition-colors"
                >
                  {submitting ? '등록 중...' : '등록'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
