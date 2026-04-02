import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts'
import { ArrowLeft, Cpu } from 'iconsax-react'
import { api } from '../api/client'

/**
 * 목적: 장비 상세 페이지. 최근 측정값 시계열 그래프를 표시합니다.
 * Route: /devices/:id
 */
export default function DeviceDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [device, setDevice] = useState(null)
  const [measurements, setMeasurements] = useState([])
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState(false)
  const [timeRange, setTimeRange] = useState('5m')  // '1m' | '5m' | 'all'
  const [thresholds, setThresholds] = useState({})   // { metric: { min, max } }
  const [savingThreshold, setSavingThreshold] = useState(false)

  useEffect(() => {
    async function load() {
      try {
        const [dev, meas] = await Promise.all([
          api.getDevice(id),
          api.getMeasurements(id, { limit: 100 }),
        ])
        setDevice(dev)
        setThresholds(dev.threshold ?? {})
        const sorted = [...meas].sort((a, b) => new Date(a.time) - new Date(b.time))
        setMeasurements(sorted)
      } catch (e) {
        console.error('장비 상세 로드 실패:', e)
      } finally {
        setLoading(false)
      }
    }
    load()

    // 5초마다 그래프 갱신
    const timer = setInterval(load, 5000)
    return () => clearInterval(timer)
  }, [id])

  async function handleSaveThreshold() {
    setSavingThreshold(true)
    try {
      await api.updateDevice(id, { threshold: thresholds })
    } catch (e) {
      console.error('임계치 저장 실패:', e)
      alert('임계치 저장에 실패했습니다.')
    } finally {
      setSavingThreshold(false)
    }
  }

  function handleThresholdChange(metric, field, value) {
    setThresholds((prev) => ({
      ...prev,
      [metric]: { ...prev[metric], [field]: value === '' ? undefined : Number(value) },
    }))
  }

  async function handleDelete() {
    if (!confirm(`"${device.name}" 장비를 삭제하시겠습니까?`)) return
    setDeleting(true)
    try {
      await api.deleteDevice(id)
      navigate('/devices')
    } catch (e) {
      console.error('장비 삭제 실패:', e)
      alert('장비 삭제에 실패했습니다.')
      setDeleting(false)
    }
  }

  if (loading) {
    return <div className="text-sm text-gray-400 mt-20 text-center">불러오는 중...</div>
  }

  if (!device) {
    return <div className="text-sm text-gray-400 mt-20 text-center">장비를 찾을 수 없습니다.</div>
  }

  // 시간 범위 필터 적용
  const rangeMs = timeRange === '1m' ? 60_000 : timeRange === '5m' ? 300_000 : Infinity
  const cutoff = Date.now() - rangeMs
  const filtered = measurements.filter((m) => new Date(m.time).getTime() >= cutoff)

  // 측정항목별로 그룹핑
  const metricGroups = filtered.reduce((acc, m) => {
    if (!acc[m.metric]) acc[m.metric] = []
    acc[m.metric].push({
      time: new Date(m.time).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
      raw: m.raw_value,
      filtered: m.filtered_value,
      unit: m.unit,
    })
    return acc
  }, {})

  const RANGE_BUTTONS = [
    { label: '1분', value: '1m' },
    { label: '5분', value: '5m' },
    { label: '전체', value: 'all' },
  ]

  return (
    <div className="max-w-4xl mx-auto">
      {/* 헤더 */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/devices')}
            className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors text-gray-400"
          >
            <ArrowLeft size={18} />
          </button>
          <div>
            <h1 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
              <Cpu size={18} color="#6b7280" />
              {device.name}
            </h1>
            <p className="text-sm text-gray-400">{device.location ?? '위치 미지정'} · {device.protocol}</p>
            <p className="text-xs text-gray-300 font-mono mt-0.5">{device.id}</p>
          </div>
        </div>
        <button
          onClick={handleDelete}
          disabled={deleting}
          className="text-xs text-red-400 hover:text-red-600 border border-red-200 hover:border-red-400 px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50"
        >
          {deleting ? '삭제 중...' : '장비 삭제'}
        </button>
      </div>

      {/* 임계치 설정 */}
      <div className="bg-white border border-gray-100 rounded-xl p-6 mb-6">
        <h2 className="text-sm font-semibold text-gray-700 mb-4">임계치 설정</h2>
        {Object.keys(metricGroups).length === 0 ? (
          <p className="text-sm text-gray-300">측정 데이터가 없어 설정할 항목이 없습니다.</p>
        ) : (
          <div className="flex flex-col gap-4">
            {Object.keys(metricGroups).map((metric) => (
              <div key={metric} className="flex items-center gap-4">
                <span className="text-sm text-gray-500 w-28 uppercase">{metric}</span>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-400">최솟값</span>
                  <input
                    type="number"
                    value={thresholds[metric]?.min ?? ''}
                    onChange={(e) => handleThresholdChange(metric, 'min', e.target.value)}
                    placeholder="없음"
                    className="w-24 border border-gray-200 rounded-lg px-2 py-1 text-sm text-center focus:outline-none focus:ring-2 focus:ring-blue-400"
                  />
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-400">최댓값</span>
                  <input
                    type="number"
                    value={thresholds[metric]?.max ?? ''}
                    onChange={(e) => handleThresholdChange(metric, 'max', e.target.value)}
                    placeholder="없음"
                    className="w-24 border border-gray-200 rounded-lg px-2 py-1 text-sm text-center focus:outline-none focus:ring-2 focus:ring-blue-400"
                  />
                </div>
              </div>
            ))}
            <button
              onClick={handleSaveThreshold}
              disabled={savingThreshold}
              className="self-start mt-1 bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 text-white text-sm px-4 py-1.5 rounded-lg transition-colors"
            >
              {savingThreshold ? '저장 중...' : '저장'}
            </button>
          </div>
        )}
      </div>

      {/* 측정항목별 그래프 */}
      {Object.keys(metricGroups).length === 0 ? (
        <div className="bg-white border border-gray-100 rounded-xl p-10 text-center text-gray-300 text-sm">
          아직 측정 데이터가 없습니다.
        </div>
      ) : (
        <>
          {/* 시간 범위 버튼 */}
          <div className="flex gap-1 mb-4">
            {RANGE_BUTTONS.map((btn) => (
              <button
                key={btn.value}
                onClick={() => setTimeRange(btn.value)}
                className={`text-xs px-3 py-1 rounded-full transition-colors ${
                  timeRange === btn.value
                    ? 'bg-blue-500 text-white'
                    : 'bg-white border border-gray-200 text-gray-500 hover:border-blue-300'
                }`}
              >
                {btn.label}
              </button>
            ))}
          </div>

          {Object.entries(metricGroups).map(([metric, data]) => (
            <div key={metric} className="bg-white border border-gray-100 rounded-xl p-6 mb-4">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">{metric}</h2>
                <span className="text-xs text-gray-400">{data[data.length - 1]?.unit ?? ''}</span>
              </div>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={data} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                  <XAxis
                    dataKey="time"
                    tick={{ fontSize: 10, fill: '#9ca3af' }}
                    interval="preserveStartEnd"
                  />
                  <YAxis tick={{ fontSize: 10, fill: '#9ca3af' }} />
                  <Tooltip
                    contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e5e7eb' }}
                    formatter={(v, name) => [
                      `${v?.toFixed(3)} ${data[0]?.unit ?? ''}`,
                      name === 'raw' ? '측정값' : '필터값',
                    ]}
                  />
                  <Line type="monotone" dataKey="raw" stroke="#3b82f6" dot={false} strokeWidth={1.5} name="raw" />
                  <Line type="monotone" dataKey="filtered" stroke="#10b981" dot={false} strokeWidth={1.5} strokeDasharray="4 2" name="filtered" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ))}
        </>
      )}
    </div>
  )
}
