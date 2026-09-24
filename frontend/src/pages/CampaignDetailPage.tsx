import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Users,
  MapPin,
  Camera,
  Clock,
  ExternalLink,
  Loader2,
  ShieldCheck,
  ShieldX,
} from 'lucide-react';
import { api, type Campaign, type LocationEvent, type TrainingEvent } from '../services/api';
import StatCard from '../components/StatCard';

export default function CampaignDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [locations, setLocations] = useState<LocationEvent[]>([]);
  const [events, setEvents] = useState<TrainingEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    Promise.all([
      api.getCampaign(id),
      api.getLocations(),
      api.getEvents(),
    ]).then(([c, locs, evts]) => {
      setCampaign(c);
      setLocations(locs.filter((l) => l.campaign_id === id));
      setEvents(evts.filter((e) => e.campaign_id === id));
    }).catch(console.error).finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full">
        <Loader2 size={28} className="animate-spin" style={{ color: 'var(--purple)' }} />
      </div>
    );
  }

  if (!campaign) {
    return <p style={{ color: 'var(--red)' }}>Campaign not found.</p>;
  }

  const locGranted = locations.filter((l) => l.permission_status === 'GRANTED').length;
  const locDenied = locations.filter((l) => l.permission_status === 'DENIED').length;
  const camGranted = events.filter((e) => e.event_type === 'CAMERA_GRANTED').length;
  const camDenied = events.filter((e) => e.event_type === 'CAMERA_DENIED').length;

  return (
    <div>
      {/* Back */}
      <Link
        to="/campaigns"
        className="inline-flex items-center gap-1 text-sm mb-6 transition-colors hover:opacity-80"
        style={{ color: 'var(--purple)', textDecoration: 'none' }}
      >
        <ArrowLeft size={16} /> Back to Campaigns
      </Link>

      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <h1 className="text-2xl font-extrabold" style={{ color: 'var(--text)' }}>
            {campaign.name}
          </h1>
          <span
            className="text-xs font-semibold px-2 py-1 rounded-lg"
            style={{
              background: campaign.status === 'active' ? 'rgba(34,197,94,.12)' : 'rgba(239,68,68,.12)',
              color: campaign.status === 'active' ? 'var(--green)' : 'var(--red)',
            }}
          >
            {campaign.status.toUpperCase()}
          </span>
        </div>
        <p className="text-sm" style={{ color: 'var(--muted)' }}>{campaign.description}</p>
        <div className="flex items-center gap-4 mt-3 text-xs" style={{ color: 'var(--muted)' }}>
          <span className="flex items-center gap-1"><Clock size={13} /> Created: {campaign.created_at?.substring(0, 19)}</span>
          <span className="flex items-center gap-1"><Clock size={13} /> Expires: {campaign.expires_at?.substring(0, 19)}</span>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Participants" value={campaign.participant_count ?? 0} icon={Users} color="var(--cyan)" />
        <StatCard label="Location Granted" value={locGranted} icon={MapPin} color="var(--green)" sub={`${locDenied} denied`} />
        <StatCard label="Camera Granted" value={camGranted} icon={Camera} color="var(--gold)" sub={`${camDenied} denied`} />
        <StatCard
          label="Awareness Score"
          value={`${locations.length + camGranted + camDenied > 0 ? Math.round(((locDenied + camDenied) / (locations.length + camGranted + camDenied)) * 100) : 0}%`}
          icon={ShieldCheck}
          color="var(--purple)"
        />
      </div>

      {/* Location events table */}
      <div
        className="rounded-2xl border p-6 mb-6"
        style={{ background: 'var(--surface)', borderColor: 'var(--border)' }}
      >
        <h3 className="text-sm font-bold mb-4 flex items-center gap-2" style={{ color: 'var(--text)' }}>
          <MapPin size={16} style={{ color: 'var(--green)' }} /> Location Permission Events
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr style={{ color: 'var(--muted)', borderBottom: '1px solid var(--border)' }}>
                <th className="text-left py-2 px-3 font-medium">Participant</th>
                <th className="text-left py-2 px-3 font-medium">Status</th>
                <th className="text-left py-2 px-3 font-medium">Coordinates</th>
                <th className="text-left py-2 px-3 font-medium">Map</th>
                <th className="text-left py-2 px-3 font-medium">Time</th>
              </tr>
            </thead>
            <tbody>
              {locations.map((loc) => (
                <tr key={loc.id} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td className="py-3 px-3 font-mono text-xs" style={{ color: 'var(--text)' }}>
                    {loc.participant_id.substring(0, 10)}
                  </td>
                  <td className="py-3 px-3">
                    <span
                      className="inline-flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-lg"
                      style={{
                        background: loc.permission_status === 'GRANTED' ? 'rgba(34,197,94,.12)' : 'rgba(239,68,68,.12)',
                        color: loc.permission_status === 'GRANTED' ? 'var(--green)' : 'var(--red)',
                      }}
                    >
                      {loc.permission_status === 'GRANTED' ? <ShieldCheck size={12} /> : <ShieldX size={12} />}
                      {loc.permission_status}
                    </span>
                  </td>
                  <td className="py-3 px-3 font-mono text-xs" style={{ color: 'var(--muted)' }}>
                    {loc.latitude && loc.longitude
                      ? `${loc.latitude.toFixed(4)}, ${loc.longitude.toFixed(4)}`
                      : '—'}
                  </td>
                  <td className="py-3 px-3">
                    {loc.latitude && loc.longitude ? (
                      <a
                        href={`https://maps.google.com/?q=${loc.latitude},${loc.longitude}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs flex items-center gap-1"
                        style={{ color: 'var(--cyan)' }}
                      >
                        <ExternalLink size={12} /> View
                      </a>
                    ) : (
                      <span className="text-xs" style={{ color: 'var(--muted)' }}>—</span>
                    )}
                  </td>
                  <td className="py-3 px-3 text-xs" style={{ color: 'var(--muted)' }}>
                    {loc.timestamp?.substring(0, 19)}
                  </td>
                </tr>
              ))}
              {locations.length === 0 && (
                <tr>
                  <td colSpan={5} className="text-center py-8" style={{ color: 'var(--muted)' }}>
                    No location events recorded.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* All events */}
      <div
        className="rounded-2xl border p-6"
        style={{ background: 'var(--surface)', borderColor: 'var(--border)' }}
      >
        <h3 className="text-sm font-bold mb-4 flex items-center gap-2" style={{ color: 'var(--text)' }}>
          <Clock size={16} style={{ color: 'var(--cyan)' }} /> All Events
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr style={{ color: 'var(--muted)', borderBottom: '1px solid var(--border)' }}>
                <th className="text-left py-2 px-3 font-medium">Event</th>
                <th className="text-left py-2 px-3 font-medium">Participant</th>
                <th className="text-left py-2 px-3 font-medium">Time</th>
              </tr>
            </thead>
            <tbody>
              {events.slice(0, 50).map((evt) => (
                <tr key={evt.id} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td className="py-3 px-3">
                    <span
                      className="inline-block text-xs font-semibold px-2 py-1 rounded-lg"
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
                    {evt.participant_id.substring(0, 10)}
                  </td>
                  <td className="py-3 px-3 text-xs" style={{ color: 'var(--muted)' }}>
                    {evt.timestamp?.substring(0, 19)}
                  </td>
                </tr>
              ))}
              {events.length === 0 && (
                <tr>
                  <td colSpan={3} className="text-center py-8" style={{ color: 'var(--muted)' }}>
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
