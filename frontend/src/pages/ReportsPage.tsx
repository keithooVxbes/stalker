import { useEffect, useState } from 'react';
import { FileText, Download, Loader2 } from 'lucide-react';
import { api, type Campaign } from '../services/api';

export default function ReportsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState<string | null>(null);

  useEffect(() => {
    api.getCampaigns().then(setCampaigns).catch(console.error).finally(() => setLoading(false));
  }, []);

  const generate = async (campaignId: string, format: 'html' | 'json') => {
    setGenerating(campaignId);
    try {
      const data = await api.getReport(campaignId, format);
      // Download as file
      let blob: Blob;
      let filename: string;
      if (format === 'html' && typeof data === 'object' && 'html' in data) {
        blob = new Blob([data.html as string], { type: 'text/html' });
        filename = `stalker_report_${campaignId.substring(0, 8)}.html`;
      } else {
        blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        filename = `stalker_report_${campaignId.substring(0, 8)}.json`;
      }
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
    } finally {
      setGenerating(null);
    }
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-extrabold" style={{ color: 'var(--text)' }}>Reports</h1>
        <p className="text-sm mt-1" style={{ color: 'var(--muted)' }}>Generate security awareness reports</p>
      </div>

      {loading ? (
        <div className="flex justify-center py-16">
          <Loader2 size={28} className="animate-spin" style={{ color: 'var(--purple)' }} />
        </div>
      ) : campaigns.length === 0 ? (
        <div className="text-center py-16" style={{ color: 'var(--muted)' }}>
          <FileText size={48} className="mx-auto mb-4 opacity-30" />
          <p>No campaigns to generate reports for.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {campaigns.map((c) => (
            <div
              key={c.id}
              className="flex items-center justify-between rounded-2xl border p-5 transition-all hover:scale-[1.005]"
              style={{ background: 'var(--surface)', borderColor: 'var(--border)' }}
            >
              <div className="flex-1 min-w-0">
                <h3 className="font-bold truncate" style={{ color: 'var(--text)' }}>{c.name}</h3>
                <p className="text-xs mt-1" style={{ color: 'var(--muted)' }}>
                  {c.participant_count ?? 0} participants &middot; {c.status}
                </p>
              </div>
              <div className="flex gap-2 ml-4">
                <button
                  onClick={() => generate(c.id, 'html')}
                  disabled={generating === c.id}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-white cursor-pointer transition-transform hover:scale-105 disabled:opacity-50"
                  style={{ background: 'linear-gradient(135deg, var(--purple), var(--pink))' }}
                >
                  {generating === c.id ? <Loader2 size={14} className="animate-spin" /> : <Download size={14} />}
                  HTML
                </button>
                <button
                  onClick={() => generate(c.id, 'json')}
                  disabled={generating === c.id}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold cursor-pointer transition-transform hover:scale-105 disabled:opacity-50 border"
                  style={{ borderColor: 'var(--border)', color: 'var(--text)', background: 'transparent' }}
                >
                  {generating === c.id ? <Loader2 size={14} className="animate-spin" /> : <Download size={14} />}
                  JSON
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
