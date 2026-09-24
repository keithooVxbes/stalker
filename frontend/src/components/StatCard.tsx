import { type LucideIcon } from 'lucide-react';

interface Props {
  label: string;
  value: string | number;
  icon: LucideIcon;
  color: string;
  sub?: string;
}

export default function StatCard({ label, value, icon: Icon, color, sub }: Props) {
  return (
    <div
      className="rounded-2xl p-5 border transition-transform hover:scale-[1.02]"
      style={{
        background: 'var(--surface)',
        borderColor: 'var(--border)',
      }}
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-medium" style={{ color: 'var(--muted)' }}>
          {label}
        </span>
        <div
          className="w-9 h-9 rounded-xl flex items-center justify-center"
          style={{ background: `${color}18` }}
        >
          <Icon size={18} style={{ color }} />
        </div>
      </div>
      <div className="text-3xl font-extrabold" style={{ color }}>
        {value}
      </div>
      {sub && (
        <span className="text-xs mt-1 block" style={{ color: 'var(--muted)' }}>
          {sub}
        </span>
      )}
    </div>
  );
}
