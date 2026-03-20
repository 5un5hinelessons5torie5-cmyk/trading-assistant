import { useState, useEffect } from 'react';
import axios from 'axios';
import {
  LayoutDashboard, Activity, FlaskConical, ListChecks, History, Zap, Shield, TrendingUp, BarChart3, Settings, ExternalLink, Filter, Tags, MessageSquare, Download, Bell, ShoppingCart, Key, ShieldCheck, ArrowRight, AlertTriangle
} from 'lucide-react';

const API_BASE = 'http://localhost:8000';

const Badge = ({ status, children }: any) => {
  const styles: any = {
    live_ready: 'bg-success/10 text-success border-success/20',
    research_only: 'bg-warning/10 text-warning border-warning/20',
    blocked: 'bg-danger/10 text-danger border-danger/20',
    active: 'bg-primary/10 text-primary border-primary/20',
    used: 'bg-secondary text-muted-foreground border-border'
  };
  return <span className={`text-[9px] font-black uppercase px-2 py-0.5 rounded border shadow-sm ${styles[status] || styles.used}`}>{children}</span>;
}

const Panel = ({ title, children, icon: Icon }: any) => (
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

const Stat = ({ label, value, subtext, color = 'text-foreground' }: any) => (
  <div className="bg-card border border-border p-6 rounded-xl shadow-md border-b-4 border-b-primary/20">
    <div className="text-[10px] font-black text-muted-foreground uppercase tracking-[0.2em] mb-4 opacity-50">{label}</div>
    <div className={`text-3xl font-black tracking-tighter ${color}`}>{value}</div>
    {subtext && <div className="text-[10px] font-bold opacity-30 uppercase mt-2 tracking-widest">{subtext}</div>}
  </div>
);

const App = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedPosition, setSelectedPosition] = useState<any>(null);
  const [symbols, setSymbols] = useState([]);
  const [signals, setSignals] = useState([]);
  const [queue, setQueue] = useState([]);
  const [positions, setPositions] = useState([]);
  const [experiments, setExperiments] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [settings, setSettings] = useState<any>(null);
  const [analyticsData, setAnalyticsData] = useState<any>(null);
  const [brokerAccounts, setBrokerAccounts] = useState([]);
  const [challenger, setChallenger] = useState<any>(null);

  const fetchData = async () => {
    try {
      const [symRes, sigRes, qRes, posRes, expRes, setRes, anaRes, alRes, bkRes] = await Promise.all([
        axios.get(`${API_BASE}/brokers/symbols`),
        axios.get(`${API_BASE}/strategies/signals`),
        axios.get(`${API_BASE}/execution/queue`),
        axios.get(`${API_BASE}/management/positions`),
        axios.get(`${API_BASE}/validation/experiments`),
        axios.get(`${API_BASE}/system/settings`),
        axios.get(`${API_BASE}/analytics/summary`),
        axios.get(`${API_BASE}/alerts/?unread_only=false`),
        axios.get(`${API_BASE}/brokers/accounts`)
      ]);
      setSymbols(symRes.data);
      setSignals(sigRes.data);
      setQueue(qRes.data);
      setPositions(posRes.data);
      setExperiments(expRes.data);
      setSettings(setRes.data);
      setAnalyticsData(anaRes.data);
      setAlerts(alRes.data);
      setBrokerAccounts(bkRes.data);
    } catch (err) { console.error(err); }
  };

  useEffect(() => {
    fetchData();
    const timer = setInterval(fetchData, 10000);
    return () => clearInterval(timer);
  }, []);

  const toggleKillSwitch = async () => {
    await axios.post(`${API_BASE}/system/kill-switch`);
    fetchData();
  };

  const exportState = async () => {
     const res = await axios.get(`${API_BASE}/system/export`);
     const blob = new Blob([JSON.stringify(JSON.parse(res.data), null, 2)], { type: 'application/json' });
     const url = URL.createObjectURL(blob);
     const link = document.createElement('a');
     link.href = url;
     link.download = `workstation_backup_${new Date().toISOString().split('T')[0]}.json`;
     link.click();
  };

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden font-sans">
      <aside className="w-64 bg-card border-r border-border flex flex-col shrink-0">
        <div className="p-6 border-b border-border">
          <div className="flex items-center gap-2 mb-1">
            <Zap className="text-primary fill-primary" size={24} />
            <h1 className="text-lg font-black tracking-tighter uppercase">Workstation</h1>
          </div>
          <p className="text-[10px] text-muted-foreground font-bold uppercase tracking-widest opacity-50">Commissioning Grade</p>
        </div>
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          <NavItem active={activeTab === 'dashboard'} onClick={() => setActiveTab('dashboard')} icon={<LayoutDashboard size={18}/>} label="Cockpit" />
          <NavItem active={activeTab === 'signals'} onClick={() => setActiveTab('signals')} icon={<Activity size={18}/>} label="Strategy Lab" />
          <NavItem active={activeTab === 'queue'} onClick={() => setActiveTab('queue')} icon={<ListChecks size={18}/>} label="Execution Queue" />
          <NavItem active={activeTab === 'orders'} onClick={() => setActiveTab('orders')} icon={<ShoppingCart size={18}/>} label="Orders" />
          <NavItem active={activeTab === 'positions'} onClick={() => setActiveTab('positions')} icon={<Shield size={18}/>} label="Positions" />
          <NavItem active={activeTab === 'lab'} onClick={() => setActiveTab('lab')} icon={<FlaskConical size={18}/>} label="Validation" />
          <NavItem active={activeTab === 'analytics'} onClick={() => setActiveTab('analytics')} icon={<BarChart3 size={18}/>} label="Analytics" />
          <NavItem active={activeTab === 'alerts'} onClick={() => setActiveTab('alerts')} icon={<Bell size={18}/>} label="Alerts" />
          <NavItem active={activeTab === 'journal'} onClick={() => setActiveTab('journal')} icon={<History size={18}/>} label="Journal" />
          <NavItem active={activeTab === 'brokers'} onClick={() => setActiveTab('brokers')} icon={<Key size={18}/>} label="Brokers" />
        </nav>
        <div className="p-4 border-t border-border bg-background/30">
          <button onClick={exportState} className="w-full flex items-center justify-center gap-2 py-2 mb-4 bg-secondary/50 hover:bg-secondary rounded text-[10px] font-black uppercase tracking-widest transition-colors border border-border">
             <Download size={14}/> Export Backup
          </button>
          <div className="flex items-center justify-between mb-4 px-2">
            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">Kill Switch</span>
            <button onClick={toggleKillSwitch} className={`w-10 h-5 rounded-full relative transition-colors ${settings?.kill_switch ? 'bg-danger shadow-lg shadow-danger/20' : 'bg-secondary'}`}>
              <div className={`absolute top-1 w-3 h-3 bg-white rounded-full transition-all ${settings?.kill_switch ? 'left-6' : 'left-1'}`} />
            </button>
          </div>
          <div className="flex items-center gap-2 px-3 py-2 rounded bg-success/10 border border-success/20">
            <div className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
            <span className="text-[10px] font-bold text-success uppercase">Exness Live</span>
          </div>
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-14 border-b border-border bg-card/50 flex items-center justify-between px-8 shrink-0 backdrop-blur">
          <div className="flex items-center gap-6 text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
             <div className="flex items-center gap-2">Status: <span className="text-success">Supervised</span></div>
             <div className="flex items-center gap-2">Active Presets: <span className="text-primary">{experiments.filter((e:any) => e.is_active).length}</span></div>
             <div className="flex items-center gap-2">Risk: <span className="text-warning">{settings?.daily_loss_stop_pct}% Stop</span></div>
          </div>
          <div className="flex items-center gap-4">
            <Settings size={16} className="text-muted-foreground cursor-pointer hover:text-foreground transition-colors" />
            <div className="w-8 h-8 rounded bg-primary/20 border border-primary/40 flex items-center justify-center text-primary font-bold text-xs shadow-inner shadow-primary/10">OP</div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-8">
          <div className="max-w-6xl mx-auto">
            {activeTab === 'dashboard' && (
              <div className="space-y-8">
                <div className="grid grid-cols-4 gap-4">
                  <Stat label="Live Universe" value={symbols.filter((s:any) => s.status === 'live_ready').length} subtext={`of ${symbols.length} tracked`} />
                  <Stat label="Approval Needed" value={queue.filter((q:any) => q.status === 'active').length} color="text-warning" />
                  <Stat label="Open PnL" value={`$${positions.filter((p:any) => p.status === 'open').reduce((acc:number, p:any) => acc + p.pnl, 0).toFixed(2)}`} color="text-success" />
                  <Stat label="System Trust" value="89%" subtext="OOS Performance" color="text-primary" />
                </div>
                <div className="grid grid-cols-2 gap-6">
                   <Panel title="Market Eligibility">
                      <div className="space-y-2 max-h-[400px] overflow-y-auto pr-2">
                        {symbols.map((s:any) => (
                          <div key={s.id} className="flex items-center justify-between p-3 bg-secondary/10 rounded border border-border/50 text-xs hover:border-primary/30 transition-colors group">
                            <div>
                               <div className="font-mono font-bold flex items-center gap-2">{s.name} <ExternalLink size={10} className="opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"/></div>
                               {s.blocked_reason && <div className="text-[9px] text-danger opacity-70 font-bold uppercase tracking-tighter">{s.blocked_reason}</div>}
                            </div>
                            <div className="flex items-center gap-3">
                              <span className="opacity-30 text-[9px] font-bold uppercase tracking-widest">{s.asset_group}</span>
                              <Badge status={s.status}>{s.status}</Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                   </Panel>
                   <Panel title="Validation Health">
                      <div className="space-y-3">
                         {experiments.map((e:any) => (
                           <div key={e.id} className={`p-4 rounded border transition-all ${e.is_active ? 'border-primary/50 bg-primary/5 shadow-lg shadow-primary/5' : 'border-border bg-secondary/5 hover:border-border-foreground/30'}`}>
                              <div className="flex justify-between items-start mb-3">
                                <div>
                                  <div className="text-xs font-black uppercase tracking-tight">{e.preset_name}</div>
                                  <div className="text-[10px] text-muted-foreground font-mono opacity-60">{e.strategy_id}</div>
                                </div>
                                <div className="text-right">
                                  <div className="text-sm font-black text-primary">{(e.oos_winrate * 100).toFixed(1)}% WR</div>
                                  <div className="text-[9px] uppercase font-black tracking-widest opacity-30">OOS Evidence</div>
                                </div>
                              </div>
                              <div className="w-full h-1.5 bg-background rounded-full overflow-hidden border border-border">
                                 <div className={`h-full transition-all ${e.trust_score > 0.7 ? 'bg-primary' : 'bg-warning'}`} style={{width: `${e.trust_score * 100}%`}}></div>
                              </div>
                           </div>
                         ))}
                      </div>
                   </Panel>
                </div>
              </div>
            )}

            {activeTab === 'signals' && (
              <div className="space-y-6">
                <Panel title="Lab Configuration">
                  <div className="grid grid-cols-4 gap-4">
                    <div className="space-y-2">
                       <label className="text-[9px] font-black uppercase tracking-widest text-muted-foreground">Broker</label>
                       <select className="w-full bg-background border border-border rounded px-3 py-2 text-xs">
                          <option>Exness MT5</option>
                          <option>Paper Broker</option>
                       </select>
                    </div>
                    <div className="space-y-2">
                       <label className="text-[9px] font-black uppercase tracking-widest text-muted-foreground">Strategy</label>
                       <select className="w-full bg-background border border-border rounded px-3 py-2 text-xs">
                          <option>EMA Pullback</option>
                          <option>Breakout Retest</option>
                          <option>Donchian Follow</option>
                       </select>
                    </div>
                    <div className="space-y-2">
                       <label className="text-[9px] font-black uppercase tracking-widest text-muted-foreground">Scan Mode</label>
                       <select className="w-full bg-background border border-border rounded px-3 py-2 text-xs" id="scan_mode_selector" onChange={(e) => {
                          const tf = document.getElementById('tf_selector') as HTMLSelectElement;
                          if (e.target.value === 'Auto Best Setup') tf.disabled = true;
                          else tf.disabled = false;
                       }}>
                          <option>Manual Scan</option>
                          <option>Auto Best Setup</option>
                       </select>
                    </div>
                    <div className="space-y-2">
                       <label className="text-[9px] font-black uppercase tracking-widest text-muted-foreground">Timeframe</label>
                       <select className="w-full bg-background border border-border rounded px-3 py-2 text-xs" id="tf_selector">
                          <option>M5</option><option>M15</option><option selected>H1</option><option>H4</option>
                       </select>
                    </div>
                  </div>
                  <div className="grid grid-cols-4 gap-4 mt-4">
                    <div className="space-y-2">
                       <label className="text-[9px] font-black uppercase tracking-widest text-muted-foreground">Bar Count</label>
                       <input type="number" defaultValue="500" className="w-full bg-background border border-border rounded px-3 py-2 text-xs"/>
                    </div>
                    <div className="space-y-2">
                       <label className="text-[9px] font-black uppercase tracking-widest text-muted-foreground">Min Queue Quality</label>
                       <input type="range" min="0" max="1" step="0.1" className="w-full accent-primary mt-2"/>
                    </div>
                    <div className="flex items-end gap-3 pb-1">
                       <button onClick={async () => {
                          const scanMode = (document.getElementById('scan_mode_selector') as HTMLSelectElement).value;
                          const tf = (document.getElementById('tf_selector') as HTMLSelectElement).value;
                          if (scanMode === 'Auto Best Setup') {
                             await axios.post(`${API_BASE}/strategies/auto-best-setup/EURUSD?timeframes=M15,H1,H4`);
                          } else {
                             await axios.post(`${API_BASE}/strategies/scan/EURUSD/${tf}`);
                          }
                          fetchData();
                       }} className="flex-1 bg-primary text-white py-2 rounded font-black uppercase text-[10px] tracking-widest">Start Scan</button>
                       <div className="flex items-center gap-2 mb-2">
                          <input type="checkbox" id="save_sig"/>
                          <label htmlFor="save_sig" className="text-[9px] font-black uppercase tracking-widest cursor-pointer">Save Signals</label>
                       </div>
                    </div>
                  </div>
                </Panel>

                <Panel title="Identified Signals">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-border text-muted-foreground uppercase font-black tracking-widest">
                        <th className="py-4 px-3">Strategy</th>
                        <th className="py-4 px-3">Symbol</th>
                        <th className="py-4 px-3">Side</th>
                        <th className="py-4 px-3 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border/30">
                      {signals.length === 0 ? (
                        <tr><td colSpan={4} className="py-10 text-center text-muted-foreground font-bold italic opacity-30 uppercase tracking-[0.2em]">No signals identified in lab</td></tr>
                      ) : signals.map((s:any) => (
                        <tr key={s.id} className="hover:bg-secondary/10 transition-colors">
                          <td className="py-5 px-3">
                            <div className="font-black text-sm tracking-tight">{s.strategy_label}</div>
                            <div className="text-[10px] opacity-40 uppercase">{s.strategy_id} • {s.timeframe}</div>
                          </td>
                          <td className="py-5 px-3 font-mono font-black">{s.symbol}</td>
                          <td className="py-5 px-3">
                            <span className={`font-black px-3 py-1 rounded-sm text-[10px] uppercase ${s.side === 'buy' ? 'bg-success/20 text-success border border-success/30' : 'bg-danger/20 text-danger border border-danger/30'}`}>{s.side}</span>
                          </td>
                          <td className="py-5 px-3 text-right">
                            <button onClick={() => axios.post(`${API_BASE}/execution/queue-add/${s.id}`).then(() => {fetchData(); setActiveTab('queue');})} className="bg-primary/5 text-primary border border-primary/20 px-4 py-2 rounded-md font-black uppercase text-[10px] hover:bg-primary hover:text-white transition-all shadow-sm">Add to Queue</button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </Panel>
              </div>
            )}

            {activeTab === 'queue' && (
               <Panel title="Execution Queue">
                 <div className="grid gap-4">
                    {queue.filter((q:any) => q.status === 'active').map((q:any) => (
                      <div key={q.id} className="flex items-center justify-between p-5 bg-card rounded border border-border hover:border-primary/40 transition-all shadow-sm group">
                        <div className="flex items-center gap-8">
                           <div className="w-12 h-12 bg-background border border-border rounded-lg flex items-center justify-center font-mono text-sm font-black text-muted-foreground group-hover:text-primary transition-colors">#{q.id}</div>
                           <div>
                              <div className="flex items-center gap-3 mb-1.5">
                                <span className="font-black text-base tracking-tighter">Signal #{q.signal_id}</span>
                                <Badge status={q.status}>{q.status}</Badge>
                              </div>
                              <p className="text-[10px] text-muted-foreground uppercase font-black tracking-widest opacity-40">{q.queue_admission_note}</p>
                           </div>
                        </div>
                        <div className="flex gap-2">
                          <button onClick={() => axios.post(`${API_BASE}/execution/execute/${q.id}`).then(fetchData)} disabled={q.status !== 'active' || settings?.kill_switch} className="bg-primary px-8 py-3 rounded-md text-[11px] font-black uppercase tracking-widest shadow-lg shadow-primary/20 hover:scale-[1.02] transition-all">Execute Trade</button>
                        </div>
                      </div>
                    ))}
                 </div>
               </Panel>
            )}

            {activeTab === 'lab' && (
               <div className="space-y-6">
                 <Panel title="Validation Scenarios">
                    <div className="grid grid-cols-2 gap-6">
                       {['ema_pullback', 'breakout_retest'].map(sid => (
                          <div key={sid} className="p-6 bg-secondary/10 border border-border rounded-xl flex flex-col justify-between group hover:border-primary/50 transition-all">
                             <div className="mb-8">
                                <h4 className="font-black text-lg uppercase tracking-tight mb-2">{sid.replace('_', ' ')}</h4>
                                <p className="text-xs text-muted-foreground font-bold uppercase tracking-widest opacity-50 leading-relaxed">Execute walk-forward OOS validation using live broker data.</p>
                             </div>
                             <button onClick={() => axios.post(`${API_BASE}/validation/run-backtest?strategy_id=${sid}&symbol=EURUSD`).then(fetchData)} className="w-full bg-primary py-3 rounded-lg font-black uppercase text-[11px] tracking-widest">Run Validation</button>
                          </div>
                       ))}
                    </div>
                 </Panel>

                 <Panel title="Validation Leaderboard">
                    <table className="w-full text-left text-xs">
                      <thead>
                        <tr className="border-b border-border text-muted-foreground uppercase font-black tracking-widest">
                          <th className="py-4 px-3">Preset Name</th>
                          <th className="py-4 px-3 text-center">Win Rate (OOS)</th>
                          <th className="py-4 px-3 text-right">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border/30">
                        {experiments.map((e:any) => (
                          <tr key={e.id} className="hover:bg-secondary/10 transition-colors">
                            <td className="py-5 px-3">
                               <div className="font-black uppercase tracking-tight">{e.preset_name}</div>
                               <div className="text-[10px] opacity-40 font-mono">{e.strategy_id}</div>
                            </td>
                            <td className="py-5 px-3 font-mono font-black text-sm text-primary text-center">{(e.oos_winrate * 100).toFixed(1)}%</td>
                            <td className="py-5 px-3 text-right">
                               <button onClick={() => {
                                  const active = experiments.find((exp:any) => exp.is_active && exp.strategy_id === e.strategy_id);
                                  setChallenger(e);
                               }} className="px-3 py-1.5 rounded font-black uppercase text-[9px] border border-border mr-2">Compare</button>
                               <button onClick={() => axios.post(`${API_BASE}/validation/promote/${e.id}`).then(fetchData)} className={`px-3 py-1.5 rounded font-black uppercase text-[9px] border ${e.is_active ? 'bg-success/10 text-success' : 'bg-primary/10 text-primary'}`}>
                                  {e.is_active ? 'Active' : 'Promote'}
                               </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                 </Panel>

                 {challenger && (
                    <div className="fixed inset-0 bg-background/90 backdrop-blur-md z-50 flex items-center justify-center p-8">
                       <div className="bg-card border border-border rounded-2xl w-full max-w-4xl shadow-2xl overflow-hidden">
                          <div className="p-8 border-b border-border flex justify-between items-center">
                             <h2 className="font-black text-xl uppercase tracking-widest flex items-center gap-3"><ShieldCheck className="text-primary"/> Challenger Comparison</h2>
                             <button onClick={() => setChallenger(null)} className="text-muted-foreground hover:text-foreground font-black text-2xl">×</button>
                          </div>
                          <div className="p-10 grid grid-cols-2 gap-12">
                             <div className="space-y-4">
                                <h3 className="font-black uppercase tracking-widest text-sm text-success">Challenger: {challenger.preset_name}</h3>
                                <div className="p-6 bg-background/50 border border-border rounded-xl">
                                   <div className="text-[9px] font-black text-muted-foreground uppercase mb-3">OOS Win Rate</div>
                                   <div className="text-2xl font-black text-primary tracking-tighter">{(challenger.oos_winrate * 100).toFixed(1)}%</div>
                                </div>
                             </div>
                             <div className="flex flex-col items-center justify-center opacity-30">
                                <AlertTriangle size={32} className="mb-4"/>
                                <p className="text-[10px] font-black uppercase tracking-widest">Compare metrics details</p>
                             </div>
                          </div>
                          <div className="p-8 bg-secondary/10 border-t border-border flex justify-center gap-6">
                             <button onClick={() => setChallenger(null)} className="px-10 py-4 bg-secondary border border-border rounded-xl font-black uppercase text-xs tracking-widest">Dismiss</button>
                             <button onClick={() => { axios.post(`${API_BASE}/validation/promote/${challenger.id}`).then(() => { fetchData(); setChallenger(null); }); }} className="px-12 py-4 bg-primary text-white rounded-xl font-black uppercase text-xs tracking-widest shadow-xl shadow-primary/20 flex items-center gap-3">
                                Promote Challenger <ArrowRight size={16}/>
                             </button>
                          </div>
                       </div>
                    </div>
                 )}
               </div>
            )}

            {activeTab === 'analytics' && <div className="grid grid-cols-3 gap-6"><Stat label="Closed Trades" value={analyticsData?.total_trades || 0} /><Stat label="Winrate" value={`${((analyticsData?.win_rate || 0) * 100).toFixed(1)}%`} color="text-primary" /><Stat label="PnL" value={`$${(analyticsData?.total_pnl || 0).toFixed(2)}`} color="text-success" /></div>}
            {activeTab === 'alerts' && <div className="space-y-3">{alerts.map((a:any) => <div key={a.id} className="p-4 bg-secondary/10 border border-border rounded-lg flex justify-between items-center"><div><Badge status={a.level === 'critical' ? 'blocked' : 'research_only'}>{a.level}</Badge><span className="ml-3 font-bold">{a.title}</span><p className="text-xs text-muted-foreground mt-1">{a.message}</p></div><button onClick={() => axios.post(`${API_BASE}/alerts/mark-read/${a.id}`).then(fetchData)} className="text-[9px] font-black uppercase">Read</button></div>)}</div>}
            {activeTab === 'journal' && <div className="space-y-4">{positions.filter((p:any) => p.status === 'closed').map((p:any) => <div key={p.id} className="p-5 bg-card border border-border rounded-lg flex justify-between items-center cursor-pointer" onClick={() => setSelectedPosition(p)}><div className="flex gap-4"><div className={`w-1 h-8 rounded-full ${p.pnl >= 0 ? 'bg-success' : 'bg-danger'}`}></div><div><div className="font-black uppercase tracking-tight">{p.symbol}</div><div className="text-[10px] text-muted-foreground">{p.created_at}</div></div></div><div className={`font-black ${p.pnl >= 0 ? 'text-success' : 'text-danger'}`}>{p.pnl >= 0 ? '+' : ''}${p.pnl.toFixed(2)}</div></div>)}</div>}
            {activeTab === 'brokers' && (
              <div className="grid grid-cols-2 gap-8">
                 <Panel title="Active Accounts">
                    <div className="space-y-4">
                       {brokerAccounts.map((acc:any) => (
                          <div key={acc.id} className="p-4 bg-secondary/10 border border-border rounded-lg flex justify-between items-center">
                             <div><div className="font-black uppercase">{acc.broker_name}</div><div className="text-[10px] text-muted-foreground font-mono">ID: {acc.login}</div></div>
                             <div className="flex gap-2"><button onClick={() => axios.post(`${API_BASE}/brokers/test-connection/${acc.id}`).then(r => alert(JSON.stringify(r.data)))} className="bg-primary/10 text-primary border border-primary/20 px-3 py-1 rounded text-[10px] font-black uppercase">Test</button><Badge status={acc.is_active ? 'live_ready' : 'used'}>{acc.is_active ? 'Active' : 'Disabled'}</Badge></div>
                          </div>
                       ))}
                    </div>
                 </Panel>
                 <div className="bg-secondary/5 border border-border rounded-xl p-8 space-y-4">
                    <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-primary mb-4">Link Exness MT5</h4>
                    <div className="space-y-4">
                       <input className="w-full bg-background border border-border rounded px-4 py-3 text-xs font-mono" placeholder="Login ID" id="login_id"/>
                       <input type="password" className="w-full bg-background border border-border rounded px-4 py-3 text-xs" placeholder="Password" id="password"/>
                       <input className="w-full bg-background border border-border rounded px-4 py-3 text-xs font-mono" placeholder="Server" id="server"/>
                       <button onClick={async () => {
                          const login = (document.getElementById('login_id') as HTMLInputElement).value;
                          const pwd = (document.getElementById('password') as HTMLInputElement).value;
                          const srv = (document.getElementById('server') as HTMLInputElement).value;
                          await axios.post(`${API_BASE}/brokers/accounts`, { broker_name: 'Exness', login: parseInt(login), password: pwd, server: srv, is_active: true });
                          fetchData();
                       }} className="w-full bg-primary py-4 rounded-xl font-black uppercase text-xs tracking-widest shadow-xl shadow-primary/20">Link Account</button>
                    </div>
                 </div>
              </div>
            )}
            {activeTab === 'positions' && <div className="grid gap-4">{positions.filter((p:any) => p.status === 'open').map((p:any) => <div key={p.id} className="p-5 bg-card border border-border rounded-lg flex justify-between items-center cursor-pointer" onClick={() => setSelectedPosition(p)}><div className="flex items-center gap-4"><div className={`w-1.5 h-10 rounded-full ${p.side === 'buy' ? 'bg-success' : 'bg-danger'}`}></div><div><div className="font-black text-lg font-mono">{p.symbol}</div><div className="text-[10px] font-bold text-muted-foreground uppercase">{p.side} {p.volume}L</div></div></div><div className={`text-xl font-black font-mono ${p.pnl >= 0 ? 'text-success' : 'text-danger'}`}>{p.pnl >= 0 ? '+' : ''}${p.pnl.toFixed(2)}</div></div>)}</div>}
            {activeTab === 'orders' && <table className="w-full text-left text-xs"><thead><tr className="border-b border-border text-muted-foreground uppercase font-black tracking-widest"><th className="py-4 px-3">Order ID</th><th className="py-4 px-3">Volume</th><th className="py-4 px-3">Result</th></tr></thead><tbody className="divide-y divide-border/30">{queue.map((q:any) => <tr key={q.id} className="hover:bg-secondary/10 transition-colors"><td className="py-4 px-3 font-mono font-bold">#{q.id}</td><td className="py-4 px-3 font-mono">{q.requested_volume}</td><td className="py-4 px-3 text-[10px] font-bold text-muted-foreground italic">{q.execution_message || 'N/A'}</td></tr>)}</tbody></table>}

            {selectedPosition && (
               <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-8">
                 <div className="bg-card border border-border rounded-2xl w-full max-w-3xl shadow-2xl overflow-hidden">
                    <div className="p-6 border-b border-border flex justify-between items-center bg-secondary/5">
                       <h2 className="font-black text-lg uppercase tracking-widest">Inspection: {selectedPosition.symbol}</h2>
                       <button onClick={() => setSelectedPosition(null)} className="text-muted-foreground hover:text-foreground font-black text-xl">×</button>
                    </div>
                    <div className="p-8 grid grid-cols-2 gap-8 overflow-y-auto max-h-[80vh]">
                       <div className="space-y-6">
                          <Panel title="Journal Reflection">
                             <div className="space-y-4">
                                <textarea defaultValue={selectedPosition.notes} onBlur={(e) => axios.post(`${API_BASE}/management/update-position/${selectedPosition.id}?notes=${e.target.value}`)} className="w-full bg-background border border-border rounded-lg p-4 text-xs h-32 focus:border-primary outline-none transition-colors" placeholder="Describe setup context..."></textarea>
                                <div className="grid grid-cols-2 gap-4">
                                   <div><label className="text-[9px] font-black text-muted-foreground uppercase mb-2 block tracking-widest">Discipline</label><div className="flex gap-1">{[1,2,3,4,5].map(s => <button key={s} onClick={() => axios.post(`${API_BASE}/management/update-position/${selectedPosition.id}?discipline_score=${s}`).then(fetchData)} className={`flex-1 h-8 rounded bg-background border text-[10px] font-black hover:border-primary transition-all ${selectedPosition.discipline_score === s ? 'border-primary text-primary shadow-lg shadow-primary/20' : 'border-border'}`}>{s}</button>)}</div></div>
                                   <div><label className="text-[9px] font-black text-muted-foreground uppercase mb-2 block tracking-widest">Setup Quality</label><div className="flex gap-1">{[1,2,3,4,5].map(s => <button key={s} onClick={() => axios.post(`${API_BASE}/management/update-position/${selectedPosition.id}?setup_quality_score=${s}`).then(fetchData)} className={`flex-1 h-8 rounded bg-background border text-[10px] font-black hover:border-primary transition-all ${selectedPosition.setup_quality_score === s ? 'border-primary text-primary shadow-lg shadow-primary/20' : 'border-border'}`}>{s}</button>)}</div></div>
                                </div>
                             </div>
                          </Panel>
                       </div>
                       <div className="space-y-6">
                          <Panel title="Live Targets">
                             <div className="space-y-3">{[{ label: 'TP1', price: selectedPosition.entry_price * 1.01, hit: true }, { label: 'TP2', price: selectedPosition.entry_price * 1.02, hit: false }].map((tp, idx) => (<div key={idx} className={`flex items-center justify-between p-3 rounded border ${tp.hit ? 'bg-success/5 border-success/30' : 'bg-background border-border'}`}><div className="flex items-center gap-3"><div className={`w-2 h-2 rounded-full ${tp.hit ? 'bg-success' : 'bg-muted-foreground opacity-30'}`}></div><span className="text-[10px] font-black uppercase">{tp.label}</span></div><span className="font-mono text-[10px] font-bold">{tp.price.toFixed(5)}</span></div>))}</div>
                          </Panel>
                          <div className="grid grid-cols-2 gap-4"><button className="py-4 bg-danger/10 text-danger border border-danger/20 rounded-xl font-black uppercase text-[10px] tracking-widest hover:bg-danger hover:text-white transition-all shadow-lg shadow-danger/5">Panic Close</button><button onClick={() => setSelectedPosition(null)} className="py-4 bg-primary text-white rounded-xl font-black uppercase text-[10px] tracking-widest shadow-lg shadow-primary/20 hover:brightness-110 transition-all">Save Changes</button></div>
                       </div>
                    </div>
                 </div>
               </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

const NavItem = ({ icon, label, active, onClick }: any) => (
  <button onClick={onClick} className={`w-full flex items-center gap-3 px-3 py-3 rounded-md transition-all ${active ? 'bg-primary/15 text-primary shadow-sm border border-primary/20' : 'text-muted-foreground hover:bg-secondary/50 hover:text-foreground'}`}>
    <span className={active ? 'text-primary' : 'text-muted-foreground opacity-40'}>{icon}</span>
    <span className={`text-xs font-black uppercase tracking-tight ${active ? 'opacity-100' : 'opacity-70'}`}>{label}</span>
  </button>
);

export default App;
