import { useEffect, useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { Target, Plus, Users, Clock, Loader2 } from 'lucide-react';
import { api, type Campaign } from '../services/api';

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: '', description: '', duration_hours: 24 });
  const [creating, setCreating] = useState(false);

  const load = () => {
    api.getCampaigns().then(setCampaigns).catch(console.error).finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault();
    setCreating(true);
    try {
      await api.createCampaign(form);
      setShowCreate(false);
      setForm({ name: '', description: '', duration_hours: 24 });
      load();
    } catch (err) {
      console.error(err);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-extrabold" style={{ color: 'var(--text)' }}>Campaigns</h1>
          <p className="text-sm mt-1" style={{ color: 'var(--muted)' }}>Manage training campaigns</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 px-5 py-3 rounded-xl text-sm font-bold text-white cursor-pointer transition-transform hover:scale-105"
          style={{ background: 'linear-gradient(135deg, var(--purple), var(--pink))' }}
        >
          <Plus size={16} /> New Campaign
        </button>
      </div>

      {/* Create modal */}
      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={() => setShowCreate(false)}>
          <form
            onClick={(e) => e.stopPropagation()}
            onSubmit={handleCreate}
            className="w-full max-w-md rounded-2xl border p-6 space-y-4"
            style={{ background: 'var(--surface)', borderColor: 'var(--border)' }}
          >
            <h2 className="text-lg font-bold" style={{ color: 'var(--text)' }}>Create Campaign</h2>
            <input
              type="text"
              placeholder="Campaign name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border text-sm outline-none"
              style={{ background: 'var(--bg)', borderColor: 'var(--border)', color: 'var(--text)' }}
              required
            />
            <textarea
              placeholder="Description"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border text-sm outline-none resize-none h-24"
              style={{ background: 'var(--bg)', borderColor: 'var(--border)', color: 'var(--text)' }}
            />
            <input
              type="number"
              placeholder="Duration (hours)"
              value={form.duration_hours}
              onChange={(e) => setForm({ ...form, duration_hours: Number(e.target.value) })}
              className="w-full px-4 py-3 rounded-xl border text-sm outline-none"
              style={{ background: 'var(--bg)', borderColor: 'var(--border)', color: 'var(--text)' }}
              min={1}
            />
            <div className="flex gap-3">
              <button
                type="submit"
                disabled={creating}
                className="flex-1 py-3 rounded-xl font-bold text-white text-sm cursor-pointer disabled:opacity-50"
                style={{ background: 'linear-gradient(135deg, var(--green), #16a34a)' }}
              >
                {creating ? <Loader2 size={16} className="animate-spin mx-auto" /> : 'Create'}
              </button>
              <button
                type="button"
                onClick={() => setShowCreate(false)}
                className="flex-1 py-3 rounded-xl font-bold text-sm cursor-pointer border"
                style={{ borderColor: 'var(--border)', color: 'var(--muted)', background: 'transparent' }}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Campaign list */}
      {loading ? (
        <div className="flex justify-center py-16">
          <Loader2 size={28} className="animate-spin" style={{ color: 'var(--purple)' }} />
        </div>
      ) : campaigns.length === 0 ? (
        <div className="text-center py-16" style={{ color: 'var(--muted)' }}>
          <Target size={48} className="mx-auto mb-4 opacity-30" />
          <p>No campaigns yet. Create your first one.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {campaigns.map((c) => (
            <Link
              key={c.id}
              to={`/campaign/${c.id}`}
              className="block rounded-2xl border p-5 transition-all hover:scale-[1.01]"
              style={{
                background: 'var(--surface)',
                borderColor: 'var(--border)',
                textDecoration: 'none',
              }}
            >
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-base font-bold truncate" style={{ color: 'var(--text)' }}>
                  {c.name}
                </h3>
                <span
                  className="text-xs font-semibold px-2 py-1 rounded-lg"
                  style={{
                    background: c.status === 'active' ? 'rgba(34,197,94,.12)' : 'rgba(239,68,68,.12)',
                    color: c.status === 'active' ? 'var(--green)' : 'var(--red)',
                  }}
                >
                  {c.status.toUpperCase()}
                </span>
              </div>
              <p className="text-xs mb-4 line-clamp-2" style={{ color: 'var(--muted)' }}>
                {c.description || 'No description'}
              </p>
              <div className="flex items-center gap-4 text-xs" style={{ color: 'var(--muted)' }}>
                <span className="flex items-center gap-1">
                  <Users size={13} /> {c.participant_count ?? 0}
                </span>
                <span className="flex items-center gap-1">
                  <Clock size={13} /> {c.created_at?.substring(0, 10)}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
