import { useEffect, useState } from 'react';
import {
  Target,
  Users,
  MapPin,
  Camera,
  Activity,

  ShieldCheck,
  ShieldX,
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import StatCard from '../components/StatCard';
import { api, type DashboardStats } from '../services/api';

const PIE_COLORS = ['#22c55e', '#ef4444'];

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getDashboardStats().then(setStats).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Activity size={32} className="animate-spin" style={{ color: 'var(--purple)' }} />
      </div>
    );
  }

  if (!stats) {
    return <p style={{ color: 'var(--muted)' }}>Failed to load dashboard data.</p>;
  }

  const locationData = [
    { name: 'Granted', value: stats.location_granted },
    { name: 'Denied', value: stats.location_denied },
  ];
  const cameraData = [
    { name: 'Granted', value: stats.camera_granted },
    { name: 'Denied', value: stats.camera_denied },
  ];

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-extrabold" style={{ color: 'var(--text)' }}>
          Dashboard
        </h1>
        <p className="text-sm mt-1" style={{ color: 'var(--muted)' }}>
          Security Operations Center Overview
        </p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          label="Active Campaigns"
          value={stats.active_campaigns}
          icon={Target}
          color="var(--purple)"
          sub={`${stats.total_campaigns} total`}
        />
        <StatCard
          label="Participants"
          value={stats.total_participants}
          icon={Users}
          color="var(--cyan)"
        />
        <StatCard
          label="Location Granted"
          value={stats.location_granted}
          icon={MapPin}
          color="var(--green)"
          sub={`${stats.location_denied} denied`}
        />
        <StatCard
          label="Camera Granted"
          value={stats.camera_granted}
          icon={Camera}
          color="var(--gold)"
          sub={`${stats.camera_denied} denied`}
        />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Location pie */}
        <div
          className="rounded-2xl border p-6"
          style={{ background: 'var(--surface)', borderColor: 'var(--border)' }}
        >
          <h3 className="text-sm font-bold mb-4 flex items-center gap-2" style={{ color: 'var(--text)' }}>
            <MapPin size={16} style={{ color: 'var(--green)' }} />
            Location Permission
          </h3>
          <div className="h-52">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={locationData}
                  cx="50%" cy="50%"
                  innerRadius={50} outerRadius={80}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {locationData.map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: 'var(--surface-2)',
                    border: '1px solid var(--border)',
                    borderRadius: '10px',
                    color: 'var(--text)',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-6 mt-2 text-xs" style={{ color: 'var(--muted)' }}>
            <span className="flex items-center gap-1">
              <ShieldCheck size={14} style={{ color: 'var(--green)' }} /> Granted: {stats.location_granted}
            </span>
            <span className="flex items-center gap-1">
              <ShieldX size={14} style={{ color: 'var(--red)' }} /> Denied: {stats.location_denied}
            </span>
          </div>
        </div>

        {/* Camera pie */}
        <div
          className="rounded-2xl border p-6"
          style={{ background: 'var(--surface)', borderColor: 'var(--border)' }}
        >
          <h3 className="text-sm font-bold mb-4 flex items-center gap-2" style={{ color: 'var(--text)' }}>
            <Camera size={16} style={{ color: 'var(--gold)' }} />
            Camera Permission
          </h3>
          <div className="h-52">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={cameraData}
                  cx="50%" cy="50%"
                  innerRadius={50} outerRadius={80}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {cameraData.map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: 'var(--surface-2)',
                    border: '1px solid var(--border)',
                    borderRadius: '10px',
                    color: 'var(--text)',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-6 mt-2 text-xs" style={{ color: 'var(--muted)' }}>
            <span className="flex items-center gap-1">
              <ShieldCheck size={14} style={{ color: 'var(--green)' }} /> Granted: {stats.camera_granted}
            </span>
            <span className="flex items-center gap-1">
              <ShieldX size={14} style={{ color: 'var(--red)' }} /> Denied: {stats.camera_denied}
            </span>
          </div>
        </div>
      </div>

      {/* Recent events */}
      <div
        className="rounded-2xl border p-6"
        style={{ background: 'var(--surface)', borderColor: 'var(--border)' }}
      >
        <h3 className="text-sm font-bold mb-4 flex items-center gap-2" style={{ color: 'var(--text)' }}>
          <Activity size={16} style={{ color: 'var(--cyan)' }} />
          Recent Events
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr style={{ color: 'var(--muted)', borderBottom: '1px solid var(--border)' }}>
                <th className="text-left py-2 px-3 font-medium">Event</th>
                <th className="text-left py-2 px-3 font-medium">Participant</th>
                <th className="text-left py-2 px-3 font-medium">Campaign</th>
                <th className="text-left py-2 px-3 font-medium">Time</th>
              </tr>
            </thead>
            <tbody>
              {stats.recent_events.map((evt, i) => (
                <tr
                  key={i}
                  className="transition-colors"
                  style={{ borderBottom: '1px solid var(--border)' }}
                >
                  <td className="py-3 px-3">
                    <span
                      className="inline-block px-2 py-1 rounded-lg text-xs font-semibold"
                      style={{
                        background: evt.event_type.includes('GRANTED')
                          ? 'rgba(34,197,94,.12)'
                          : evt.event_type.includes('DENIED')
                          ? 'rgba(239,68,68,.12)'
                          : 'rgba(168,85,247,.12)',
                        color: evt.event_type.includes('GRANTED')
                          ? 'var(--green)'
                          : evt.event_type.includes('DENIED')
                          ? 'var(--red)'
                          : 'var(--purple)',
                      }}
                    >
                      {evt.event_type}
                    </span>
                  </td>
                  <td className="py-3 px-3 font-mono text-xs" style={{ color: 'var(--text)' }}>
                    {evt.participant_id}
                  </td>
                  <td className="py-3 px-3 font-mono text-xs" style={{ color: 'var(--muted)' }}>
                    {evt.campaign_id}
                  </td>
                  <td className="py-3 px-3 text-xs" style={{ color: 'var(--muted)' }}>
                    {evt.timestamp?.substring(0, 19)}
                  </td>
                </tr>
              ))}
              {stats.recent_events.length === 0 && (
                <tr>
                  <td colSpan={4} className="text-center py-8" style={{ color: 'var(--muted)' }}>
                    No events yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
