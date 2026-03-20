import { TrendingUp } from 'lucide-react';

export const Badge = ({ status, children }: any) => {
  const styles: any = {
    live_ready: 'bg-success/10 text-success border-success/20',
    research_only: 'bg-warning/10 text-warning border-warning/20',
    blocked: 'bg-danger/10 text-danger border-danger/20',
    active: 'bg-primary/10 text-primary border-primary/20',
    used: 'bg-secondary text-muted-foreground border-border'
  };
  return <span className={`text-[9px] font-black uppercase px-2 py-0.5 rounded border shadow-sm ${styles[status] || styles.used}`}>{children}</span>;
}

export const Panel = ({ title, children, icon: Icon }: any) => (
  <div className="bg-card border border-border rounded-xl shadow-lg flex flex-col overflow-hidden">
    <div className="px-6 py-4 bg-secondary/5 border-b border-border flex items-center justify-between">
      <h3 className="text-xs font-black uppercase tracking-[0.15em] flex items-center gap-2">
        {Icon ? <Icon size={14} className="text-primary"/> : <TrendingUp size={14} className="text-primary"/>}
        {title}
      </h3>
      <div className="w-2 h-2 rounded-full bg-primary/20 shadow-inner"></div>
    </div>
    <div className="p-6 flex-1">{children}</div>
  </div>
);

export const Stat = ({ label, value, subtext, color = 'text-foreground' }: any) => (
  <div className="bg-card border border-border p-6 rounded-xl shadow-md border-b-4 border-b-primary/20">
    <div className="text-[10px] font-black text-muted-foreground uppercase tracking-[0.2em] mb-4 opacity-50">{label}</div>
    <div className={`text-3xl font-black tracking-tighter ${color}`}>{value}</div>
    {subtext && <div className="text-[10px] font-bold opacity-30 uppercase mt-2 tracking-widest">{subtext}</div>}
  </div>
);

export const NavItem = ({ icon, label, active, onClick }: any) => (
  <button onClick={onClick} className={`w-full flex items-center gap-3 px-3 py-3 rounded-md transition-all ${active ? 'bg-primary/15 text-primary shadow-sm border border-primary/20' : 'text-muted-foreground hover:bg-secondary/50 hover:text-foreground'}`}>
    <span className={active ? 'text-primary' : 'text-muted-foreground opacity-40'}>{icon}</span>
    <span className={`text-xs font-black uppercase tracking-tight ${active ? 'opacity-100' : 'opacity-70'}`}>{label}</span>
  </button>
);
