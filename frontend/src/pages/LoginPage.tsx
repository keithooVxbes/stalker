import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Loader2 } from 'lucide-react';
import { api } from '../services/api';

export default function LoginPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await api.login(username, password);
      localStorage.setItem('stalker_token', data.access_token);
      navigate('/dashboard');
    } catch {
      setError('Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center p-4"
      style={{ background: 'var(--bg)' }}
    >
      {/* Ambient glow */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{
          background:
            'radial-gradient(ellipse 500px 400px at 50% 40%, rgba(168,85,247,.1), transparent)',
        }}
      />

      <div
        className="relative w-full max-w-md rounded-2xl border p-8"
        style={{
          background: 'var(--surface)',
          borderColor: 'var(--border)',
          boxShadow: '0 0 80px rgba(168,85,247,.06)',
        }}
      >
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Shield size={36} style={{ color: 'var(--purple)' }} />
            <span className="text-2xl font-extrabold tracking-widest" style={{ color: 'var(--text)' }}>
              STALKER
            </span>
          </div>
          <p className="text-sm" style={{ color: 'var(--muted)' }}>
            Admin Dashboard — Authorized Access Only
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-xs font-semibold mb-2 uppercase tracking-wider" style={{ color: 'var(--muted)' }}>
              Username
            </label>
            <input
              id="input-username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 rounded-xl border text-sm outline-none transition-colors focus:border-purple-500"
              style={{
                background: 'var(--bg)',
                borderColor: 'var(--border)',
                color: 'var(--text)',
              }}
              placeholder="admin"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold mb-2 uppercase tracking-wider" style={{ color: 'var(--muted)' }}>
              Password
            </label>
            <input
              id="input-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 rounded-xl border text-sm outline-none transition-colors focus:border-purple-500"
              style={{
                background: 'var(--bg)',
                borderColor: 'var(--border)',
                color: 'var(--text)',
              }}
              placeholder="••••••••"
              required
            />
          </div>

          {error && (
            <p className="text-sm font-medium" style={{ color: 'var(--red)' }}>
              {error}
            </p>
          )}

          <button
            id="btn-login"
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl font-bold text-white text-sm transition-all hover:scale-[1.02] active:scale-[.98] cursor-pointer disabled:opacity-50"
            style={{
              background: 'linear-gradient(135deg, var(--purple), var(--pink))',
              boxShadow: '0 0 30px rgba(168,85,247,.2)',
            }}
          >
            {loading ? (
              <Loader2 size={18} className="animate-spin mx-auto" />
            ) : (
              'LOGIN'
            )}
          </button>
        </form>

        <p className="text-center text-xs mt-6" style={{ color: 'var(--muted)' }}>
          STALKER Framework v1.0.0 &middot; 0xPurpleMiaw16
        </p>
      </div>
    </div>
  );
}
