import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Database,
  BarChart3,
  CloudDownload,
  Brain,
  Settings,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  { label: 'Tableau de bord', href: '/', icon: LayoutDashboard },
  { label: 'Datasets', href: '/datasets', icon: Database },
  { label: 'Analyse', href: '/analysis', icon: BarChart3 },
  { label: 'Collecte', href: '/collection', icon: CloudDownload },
  { label: 'Modèles ML', href: '/models', icon: Brain },
  { label: 'Paramètres', href: '/settings', icon: Settings },
]

export function Sidebar() {
  return (
    <aside className="hidden md:flex flex-col w-64 border-r bg-card">
      <div className="p-6 border-b">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-cm-green flex items-center justify-center">
            <span className="text-white font-bold text-sm">CM</span>
          </div>
          <div>
            <h1 className="font-bold text-lg text-cm-green">DataCollect</h1>
            <p className="text-xs text-muted-foreground">Pro Cameroun</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.href}
              to={item.href}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-cm-green text-white'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                )
              }
            >
              <Icon className="w-4 h-4" />
              {item.label}
            </NavLink>
          )
        })}
      </nav>

      <div className="p-4 border-t">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <div className="w-2 h-2 rounded-full bg-green-500" />
          <span>Système opérationnel</span>
        </div>
        <p className="text-xs text-muted-foreground mt-1">v1.0.0</p>
      </div>
    </aside>
  )
}
