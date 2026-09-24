import { useState, type ReactNode } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import {
  LayoutDashboard,
  Target,
  FileText,
  LogOut,
  Shield,
  Menu,

} from 'lucide-react';

interface Props { children: ReactNode; }

const NAV = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/campaigns', label: 'Campaigns', icon: Target },
  { to: '/reports',   label: 'Reports',   icon: FileText },
];

export default function Layout({ children }: Props) {
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const logout = () => {
    localStorage.removeItem('stalker_token');
    navigate('/login');
  };

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: 'var(--bg)' }}>
      {/* ── Sidebar ─────────────────────────────────────────────── */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 flex flex-col border-r transition-transform duration-300 lg:relative lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        style={{ background: 'var(--surface)', borderColor: 'var(--border)' }}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-6 py-5 border-b" style={{ borderColor: 'var(--border)' }}>
          <Shield size={28} style={{ color: 'var(--purple)' }} />
          <div>
            <span className="font-extrabold text-lg tracking-wide" style={{ color: 'var(--text)' }}>
              STALKER
            </span>
            <span className="block text-xs" style={{ color: 'var(--muted)' }}>Admin Panel</span>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 py-4 px-3 space-y-1">
          {NAV.map(({ to, label, icon: Icon }) => {
            const active = location.pathname.startsWith(to);
            return (
              <Link
                key={to}
                to={to}
                onClick={() => setSidebarOpen(false)}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-colors ${
                  active ? 'text-white' : ''
                }`}
                style={{
                  background: active ? 'rgba(168,85,247,.15)' : 'transparent',
                  color: active ? 'var(--purple)' : 'var(--muted)',
                }}
              >
                <Icon size={18} />
                {label}
              </Link>
            );
          })}
        </nav>

        {/* Logout */}
        <div className="p-4 border-t" style={{ borderColor: 'var(--border)' }}>
          <button
            onClick={logout}
            className="flex items-center gap-2 w-full px-4 py-3 rounded-xl text-sm font-medium transition-colors cursor-pointer"
            style={{ color: 'var(--red)' }}
          >
            <LogOut size={18} /> Logout
          </button>
        </div>
      </aside>

      {/* ── Overlay for mobile ────────────────────────────────── */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* ── Main content ──────────────────────────────────────── */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Topbar */}
        <header
          className="flex items-center justify-between px-6 py-4 border-b lg:hidden"
          style={{ background: 'var(--surface)', borderColor: 'var(--border)' }}
        >
          <button onClick={() => setSidebarOpen(true)}>
            <Menu size={24} style={{ color: 'var(--text)' }} />
          </button>
          <span className="font-bold" style={{ color: 'var(--purple)' }}>STALKER</span>
          <div style={{ width: 24 }} />
        </header>

        <main className="flex-1 overflow-y-auto p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
