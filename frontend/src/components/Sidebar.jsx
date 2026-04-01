import { NavLink } from 'react-router-dom'
import { Category2, Cpu, Notification, Activity } from 'iconsax-react'

const navItems = [
  { to: '/', icon: Category2, label: '대시보드' },
  { to: '/devices', icon: Cpu, label: '장비 관리' },
  { to: '/alerts', icon: Notification, label: '알림 내역' },
]

export default function Sidebar() {
  return (
    <aside className="w-56 bg-white border-r border-gray-100 flex flex-col py-6 px-4 shrink-0">
      {/* Logo */}
      <div className="flex items-center gap-2 px-2 mb-10">
        <Activity size={22} color="#3b82f6" variant="Bold" />
        <span className="text-base font-semibold text-gray-900 tracking-tight">LabGuard</span>
      </div>

      {/* Nav */}
      <nav className="flex flex-col gap-1">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive
                  ? 'bg-blue-50 text-blue-600 font-medium'
                  : 'text-gray-500 hover:bg-gray-50 hover:text-gray-800'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <Icon size={18} variant={isActive ? 'Bold' : 'Linear'} />
                {label}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Bottom */}
      <div className="mt-auto px-2 text-xs text-gray-300">v0.1.0</div>
    </aside>
  )
}
