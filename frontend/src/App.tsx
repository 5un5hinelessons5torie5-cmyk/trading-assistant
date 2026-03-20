import { useState, useEffect } from 'react';
import axios from 'axios';
import {
  LayoutDashboard, Activity, FlaskConical, ListChecks, History, Zap, Shield, TrendingUp, BarChart3, Settings, ExternalLink, Filter, Tags, MessageSquare, Download, Bell, ShoppingCart, Key
} from 'lucide-react';

const API_BASE = 'http://localhost:8000';

interface Symbol { id: number; name: string; status: string; asset_group: string; broker: string; blocked_reason?: string; }
interface Signal { id: number; strategy_id: string; strategy_label: string; symbol: string; timeframe: string; side: string; entry_price: number; confidence: number; ml_score: number | null; }
interface QueueItem { id: number; signal_id: number; status: string; requested_volume: number; risk_reward: number; queue_admission_note: string; created_at: string; execution_message?: string; }
interface Position { id: number; broker_ticket: string; symbol: string; side: string; volume: number; entry_price: number; current_price: number; pnl: number; status: string; stop_loss: number; take_profit: number; created_at: string; tp_ladder: string; is_paper: boolean; }
interface Experiment { id: number; strategy_id: string; preset_name: string; oos_winrate: number; trust_score: number; is_active: boolean; oos_trades_count: number; oos_profit_factor: number; }
interface Alert { id: number; category: string; level: string; title: string; message: string; is_read: boolean; created_at: string; }
interface SystemSettings { kill_switch: boolean; max_mt5_open_positions: number; daily_loss_stop_pct: number; }
interface Analytics { total_trades: number; win_rate: number; total_pnl: number; avg_pnl: number; }
interface BrokerAccount { id: number; broker_name: string; login: number; server: string; is_active: boolean; }

const App = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedPosition, setSelectedPosition] = useState<Position | null>(null);
  const [symbols, setSymbols] = useState<Symbol[]>([]);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [queue, setQueue] = useState<QueueItem[]>([]);
  const [positions, setPositions] = useState<Position[]>([]);
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [brokerAccounts, setBrokerAccounts] = useState<BrokerAccount[]>([]);

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
      setAnalytics(anaRes.data);
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

  const runBacktest = async (sid: string, sym: string) => {
     await axios.post(`${API_BASE}/validation/run-backtest?strategy_id=${sid}&symbol=${sym}`);
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
             <div className="flex items-center gap-2">Active Presets: <span className="text-primary">{experiments.filter(e => e.is_active).length}</span></div>
             <div className="flex items-center gap-2">Risk: <span className="text-warning">{settings?.daily_loss_stop_pct}% Stop</span></div>
          </div>
          <div className="flex items-center gap-4">
            <div className="relative mr-2">
               <Bell size={16} className="text-muted-foreground cursor-pointer" />
               {alerts.filter(a => !a.is_read).length > 0 && <div className="absolute -top-1 -right-1 w-2 h-2 bg-danger rounded-full" />}
            </div>
            <Settings size={16} className="text-muted-foreground cursor-pointer hover:text-foreground transition-colors" />
            <div className="w-8 h-8 rounded bg-primary/20 border border-primary/40 flex items-center justify-center text-primary font-bold text-xs shadow-inner shadow-primary/10">OP</div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-8">
          <div className="max-w-6xl mx-auto space-y-8">
            {activeTab === 'dashboard' && (
              <>
                <div className="grid grid-cols-4 gap-4">
                  <Stat label="Live Universe" value={symbols.filter(s => s.status === 'live_ready').length} subtext={`of ${symbols.length} tracked`} />
                  <Stat label="Approval Needed" value={queue.filter(q => q.status === 'active').length} color="text-warning" />
                  <Stat label="Open PnL" value={`$${positions.filter(p => p.status === 'open').reduce((acc, p) => acc + p.pnl, 0).toFixed(2)}`} color="text-success" />
                  <Stat label="System Trust" value="89%" subtext="OOS Performance" color="text-primary" />
                </div>
                <div className="grid grid-cols-2 gap-6">
                   <Panel title="Market Eligibility">
                      <div className="space-y-2 max-h-[400px] overflow-y-auto pr-2">
                        {symbols.map(s => (
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
                         {experiments.length === 0 && <div className="text-center py-10 text-muted-foreground text-xs font-bold uppercase tracking-widest opacity-30">No experiments saved</div>}
                         {experiments.map(e => (
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
                              <div className="flex items-center gap-4 text-[10px] font-bold uppercase tracking-tighter text-muted-foreground mb-3">
                                 <span>PF: <span className="text-foreground">{e.oos_profit_factor.toFixed(2)}</span></span>
                                 <span>Trades: <span className="text-foreground">{e.oos_trades_count}</span></span>
                                 <Badge status={e.is_active ? 'live_ready' : 'research_only'}>{e.is_active ? 'Active' : 'Challenger'}</Badge>
                              </div>
                              <div className="w-full h-1.5 bg-background rounded-full overflow-hidden border border-border">
                                 <div className={`h-full transition-all ${e.trust_score > 0.7 ? 'bg-primary' : 'bg-warning'}`} style={{width: `${e.trust_score * 100}%`}}></div>
                              </div>
                           </div>
                         ))}
                      </div>
                   </Panel>
                </div>
              </>
            )}

            {activeTab === 'signals' && (
              <Panel title="Identified Signals">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-border text-muted-foreground uppercase font-black tracking-widest">
                      <th className="py-4 px-3">Strategy</th>
                      <th className="py-4 px-3">Symbol</th>
                      <th className="py-4 px-3">Side</th>
                      <th className="py-4 px-3">Conf</th>
                      <th className="py-4 px-3">ML Ranking</th>
                      <th className="py-4 px-3 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/30">
                    {signals.length === 0 && <tr><td colSpan={6} className="py-20 text-center opacity-30 font-bold uppercase tracking-widest">No signals identified in last scan</td></tr>}
                    {signals.map(s => (
                      <tr key={s.id} className="hover:bg-secondary/10 transition-colors group">
                        <td className="py-5 px-3">
                          <div className="font-black text-sm tracking-tight">{s.strategy_label}</div>
                          <div className="text-[10px] opacity-40 font-bold uppercase">{s.strategy_id} • {s.timeframe}</div>
                        </td>
                        <td className="py-5 px-3 font-mono font-black text-sm">{s.symbol}</td>
                        <td className="py-5 px-3">
                          <span className={`font-black px-3 py-1 rounded-sm text-[10px] uppercase shadow-sm ${s.side === 'buy' ? 'bg-success/20 text-success border border-success/30' : 'bg-danger/20 text-danger border border-danger/30'}`}>{s.side}</span>
                        </td>
                        <td className="py-5 px-3 font-mono font-bold text-muted-foreground">{(s.confidence * 100).toFixed(0)}%</td>
                        <td className="py-5 px-3">
                          <div className="flex items-center gap-3">
                             <div className="w-16 h-2 bg-background border border-border rounded-full overflow-hidden">
                               <div className="h-full bg-primary shadow-[0_0_8px_rgba(59,130,246,0.5)]" style={{width: `${(s.ml_score || 0) * 100}%`}}></div>
                             </div>
                             <span className="font-black text-primary text-sm">{(s.ml_score || 0).toFixed(2)}</span>
                          </div>
                        </td>
                        <td className="py-5 px-3 text-right">
                          <button onClick={() => axios.post(`${API_BASE}/execution/queue-add/${s.id}`).then(() => setActiveTab('queue'))} className="bg-primary/5 text-primary border border-primary/20 px-4 py-2 rounded-md font-black uppercase text-[10px] hover:bg-primary hover:text-white transition-all shadow-sm">Add to Queue</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </Panel>
            )}

            {activeTab === 'queue' && (
               <Panel title="Active Execution Queue">
                 <div className="grid gap-4">
                    {queue.filter(q => q.status === 'active').length === 0 && <div className="py-20 text-center opacity-30 font-bold uppercase tracking-widest">No active queue items</div>}
                    {queue.filter(q => q.status === 'active').map(q => (
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
                        <div className="flex items-center gap-16 text-center">
                           <div className="min-w-[60px]">
                              <div className="text-[9px] font-black text-muted-foreground uppercase tracking-widest mb-1 opacity-50">Volume</div>
                              <div className="font-mono font-black text-sm">{q.requested_volume}</div>
                           </div>
                           <div className="min-w-[60px]">
                              <div className="text-[9px] font-black text-muted-foreground uppercase tracking-widest mb-1 opacity-50">R:R</div>
                              <div className="font-mono font-black text-sm text-primary">{q.risk_reward.toFixed(1)}</div>
                           </div>
                           <div className="flex gap-2">
                             <button onClick={() => axios.post(`${API_BASE}/execution/execute/${q.id}`).then(fetchData)} disabled={q.status !== 'active' || settings?.kill_switch} className="bg-primary px-8 py-3 rounded-md text-[11px] font-black uppercase tracking-widest disabled:opacity-30 shadow-lg shadow-primary/20 hover:scale-[1.02] active:scale-95 transition-all">Execute Trade</button>
                             <button className="p-3 bg-secondary/30 border border-border rounded-md hover:bg-secondary/50 transition-colors"><Settings size={14}/></button>
                           </div>
                        </div>
                      </div>
                    ))}
                 </div>
               </Panel>
            )}

            {activeTab === 'orders' && (
               <Panel title="Order Execution History">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-border text-muted-foreground uppercase font-black tracking-widest">
                        <th className="py-4 px-3">Order ID</th>
                        <th className="py-4 px-3">Signal</th>
                        <th className="py-4 px-3">Status</th>
                        <th className="py-4 px-3">Volume</th>
                        <th className="py-4 px-3">Result</th>
                        <th className="py-4 px-3 text-right">Timestamp</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border/30">
                      {queue.map(q => (
                        <tr key={q.id} className="hover:bg-secondary/10 transition-colors">
                          <td className="py-4 px-3 font-mono font-bold">#{q.id}</td>
                          <td className="py-4 px-3 font-bold">Signal #{q.signal_id}</td>
                          <td className="py-4 px-3"><Badge status={q.status}>{q.status}</Badge></td>
                          <td className="py-4 px-3 font-mono">{q.requested_volume}</td>
                          <td className="py-4 px-3 text-[10px] font-bold text-muted-foreground italic">{q.execution_message || 'N/A'}</td>
                          <td className="py-4 px-3 text-right text-[10px] opacity-50">{q.created_at}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
               </Panel>
            )}

            {activeTab === 'positions' && (
               <Panel title="Active Broker Positions">
                  <div className="grid gap-4">
                    {positions.filter(p => p.status === 'open').length === 0 && <div className="py-20 text-center opacity-30 font-bold uppercase tracking-widest">No open positions</div>}
                    {positions.filter(p => p.status === 'open').map(p => (
                       <div key={p.id} className="p-5 bg-card border border-border rounded-lg shadow-md flex items-center justify-between cursor-pointer hover:border-primary/30 transition-colors" onClick={() => setSelectedPosition(p)}>
                          <div className="flex items-center gap-6">
                             <div className={`w-1.5 h-10 rounded-full ${p.side === 'buy' ? 'bg-success' : 'bg-danger'}`}></div>
                             <div>
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="font-black text-lg font-mono">{p.symbol}</span>
                                  <span className={`text-[10px] font-black uppercase px-2 py-0.5 rounded border ${p.side === 'buy' ? 'bg-success/10 text-success border-success/20' : 'bg-danger/10 text-danger border-danger/20'}`}>{p.side} {p.volume}L</span>
                                </div>
                                <div className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Ticket: #{p.broker_ticket} {p.is_paper ? '(PAPER)' : '(LIVE)'}</div>
                             </div>
                          </div>
                          <div className="flex items-center gap-12">
                             <div className="text-center">
                                <div className="text-[9px] font-black text-muted-foreground uppercase tracking-widest mb-1 opacity-50">Entry</div>
                                <div className="font-mono font-bold text-xs">{p.entry_price.toFixed(5)}</div>
                             </div>
                             <div className="text-center">
                                <div className="text-[9px] font-black text-muted-foreground uppercase tracking-widest mb-1 opacity-50">Current</div>
                                <div className="font-mono font-bold text-xs">{p.current_price.toFixed(5)}</div>
                             </div>
                             <div className="text-right min-w-[100px]">
                                <div className="text-[9px] font-black text-muted-foreground uppercase tracking-widest mb-1 opacity-50">Profit/Loss</div>
                                <div className={`text-xl font-black font-mono ${p.pnl >= 0 ? 'text-success' : 'text-danger'}`}>
                                   {p.pnl >= 0 ? '+' : ''}${p.pnl.toFixed(2)}
                                </div>
                             </div>
                             <button className="bg-secondary px-4 py-2 rounded text-[10px] font-black uppercase tracking-widest border border-border hover:bg-danger hover:text-white transition-all">Close</button>
                          </div>
                       </div>
                    ))}
                  </div>
               </Panel>
            )}

            {activeTab === 'lab' && (
               <div className="space-y-6">
                 <Panel title="Validation Scenarios">
                    <div className="grid grid-cols-3 gap-6">
                       {['ema_pullback', 'breakout_retest'].map(sid => (
                          <div key={sid} className="p-6 bg-secondary/10 border border-border rounded-xl flex flex-col justify-between group hover:border-primary/50 transition-all">
                             <div className="mb-8">
                                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4 text-primary group-hover:scale-110 transition-transform"><TrendingUp size={24}/></div>
                                <h4 className="font-black text-lg uppercase tracking-tight mb-2">{sid.replace('_', ' ')}</h4>
                                <p className="text-xs text-muted-foreground font-bold uppercase tracking-widest opacity-50 leading-relaxed">Full walk-forward OOS validation against live market spreads and cost models.</p>
                             </div>
                             <button onClick={() => runBacktest(sid, 'EURUSD')} className="w-full bg-primary py-3 rounded-lg font-black uppercase text-[11px] tracking-[0.2em] shadow-lg shadow-primary/20 hover:brightness-110 transition-all">Run Validation</button>
                          </div>
                       ))}
                       <div className="p-6 border border-dashed border-border rounded-xl flex flex-col items-center justify-center text-center opacity-40 hover:opacity-100 transition-opacity cursor-pointer">
                          <div className="text-3xl font-thin mb-2">+</div>
                          <div className="text-[10px] font-black uppercase tracking-widest">Custom Preset</div>
                       </div>
                    </div>
                 </Panel>

                 <Panel title="Evidence Leaderboard">
                    <table className="w-full text-left text-xs">
                      <thead>
                        <tr className="border-b border-border text-muted-foreground uppercase font-black tracking-widest">
                          <th className="py-4 px-3">Preset Name</th>
                          <th className="py-4 px-3">Win Rate</th>
                          <th className="py-4 px-3">Profit Factor</th>
                          <th className="py-4 px-3">Trust Score</th>
                          <th className="py-4 px-3 text-right">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border/30">
                        {experiments.map(e => (
                          <tr key={e.id} className="hover:bg-secondary/10 transition-colors">
                            <td className="py-5 px-3">
                               <div className="font-black uppercase tracking-tight">{e.preset_name}</div>
                               <div className="text-[10px] opacity-40 font-mono">{e.strategy_id}</div>
                            </td>
                            <td className="py-5 px-3 font-mono font-black text-sm text-primary">{(e.oos_winrate * 100).toFixed(1)}%</td>
                            <td className="py-5 px-3 font-mono font-bold text-muted-foreground">{e.oos_profit_factor.toFixed(2)}</td>
                            <td className="py-5 px-3">
                               <div className="flex items-center gap-2">
                                  <div className="w-12 h-1 bg-background border border-border rounded-full overflow-hidden">
                                     <div className="h-full bg-primary" style={{width: `${e.trust_score * 100}%`}}></div>
                                  </div>
                                  <span className="font-bold">{(e.trust_score * 100).toFixed(0)}</span>
                               </div>
                            </td>
                            <td className="py-5 px-3 text-right">
                               <button onClick={() => axios.post(`${API_BASE}/validation/promote/${e.id}`).then(fetchData)} className={`px-3 py-1.5 rounded font-black uppercase text-[10px] border transition-all ${e.is_active ? 'bg-success/10 text-success border-success/20' : 'bg-primary/10 text-primary border-primary/20 hover:bg-primary hover:text-white'}`}>
                                  {e.is_active ? 'Active' : 'Promote'}
                               </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                 </Panel>
               </div>
            )}

            {activeTab === 'analytics' && (
               <div className="space-y-6">
                  <div className="grid grid-cols-3 gap-6">
                     <div className="bg-card border border-border p-8 rounded-xl shadow-sm">
                        <div className="text-[10px] font-black text-muted-foreground uppercase tracking-widest mb-6 border-b border-border/30 pb-4">Closed Trades</div>
                        <div className="text-5xl font-black mb-2 tracking-tighter">{analytics?.total_trades || 0}</div>
                        <div className="text-xs font-bold text-muted-foreground uppercase tracking-wider opacity-40">Total Executions</div>
                     </div>
                     <div className="bg-card border border-border p-8 rounded-xl shadow-sm">
                        <div className="text-[10px] font-black text-muted-foreground uppercase tracking-widest mb-6 border-b border-border/30 pb-4">Realized Winrate</div>
                        <div className="text-5xl font-black mb-2 tracking-tighter text-primary">{((analytics?.win_rate || 0) * 100).toFixed(1)}%</div>
                        <div className="text-xs font-bold text-muted-foreground uppercase tracking-wider opacity-40">Sample Size Adjusted</div>
                     </div>
                     <div className="bg-card border border-border p-8 rounded-xl shadow-sm">
                        <div className="text-[10px] font-black text-muted-foreground uppercase tracking-widest mb-6 border-b border-border/30 pb-4">Total P&L (USD)</div>
                        <div className={`text-5xl font-black mb-2 tracking-tighter ${(analytics?.total_pnl || 0) >= 0 ? 'text-success' : 'text-danger'}`}>
                           {(analytics?.total_pnl || 0) >= 0 ? '+' : ''}${(analytics?.total_pnl || 0).toFixed(2)}
                        </div>
                        <div className="text-xs font-bold text-muted-foreground uppercase tracking-wider opacity-40">Net After Commission</div>
                     </div>
                  </div>

                  <Panel title="Performance Breakdown">
                     <div className="h-[300px] flex items-center justify-center border border-dashed border-border rounded-lg bg-secondary/5 opacity-40">
                        <div className="text-center">
                           <BarChart3 size={48} className="mx-auto mb-4 opacity-20"/>
                           <p className="text-xs font-black uppercase tracking-[0.3em]">Advanced Metrics Coming Soon</p>
                        </div>
                     </div>
                  </Panel>
               </div>
            )}

            {activeTab === 'alerts' && (
               <Panel title="System Alerts & Warnings">
                  <div className="space-y-3">
                     {alerts.length === 0 && <div className="py-20 text-center opacity-30 font-bold uppercase tracking-widest">No system alerts</div>}
                     {alerts.map(a => (
                        <div key={a.id} className={`p-4 rounded border ${a.level === 'critical' ? 'bg-danger/5 border-danger/30' : 'bg-secondary/10 border-border'}`}>
                           <div className="flex justify-between items-start mb-2">
                              <div className="flex items-center gap-3">
                                 <Badge status={a.level === 'critical' ? 'blocked' : 'research_only'}>{a.level}</Badge>
                                 <span className="font-black text-sm uppercase tracking-tight">{a.title}</span>
                              </div>
                              <span className="text-[10px] opacity-40 font-bold">{a.created_at}</span>
                           </div>
                           <p className="text-xs text-muted-foreground leading-relaxed">{a.message}</p>
                           {!a.is_read && (
                             <button onClick={() => axios.post(`${API_BASE}/alerts/mark-read/${a.id}`).then(fetchData)} className="mt-3 text-[9px] font-black uppercase tracking-widest text-primary hover:underline">Mark as read</button>
                           )}
                        </div>
                     ))}
                  </div>
               </Panel>
            )}

            {activeTab === 'journal' && (
               <Panel title="Trading Journal">
                  <div className="flex items-center gap-4 mb-6 border-b border-border pb-6 overflow-x-auto">
                     <button className="flex items-center gap-2 px-4 py-2 bg-primary/10 text-primary border border-primary/20 rounded font-black uppercase text-[10px] tracking-widest"><Filter size={14}/> Filter History</button>
                     <button className="flex items-center gap-2 px-4 py-2 bg-secondary border border-border rounded font-black uppercase text-[10px] tracking-widest opacity-60 hover:opacity-100 transition-opacity">Export CSV</button>
                  </div>
                  <div className="space-y-4">
                    {positions.filter(p => p.status === 'closed').length === 0 && <div className="py-20 text-center opacity-30 font-bold uppercase tracking-widest">No journal entries available</div>}
                    {positions.filter(p => p.status === 'closed').map(p => (
                       <div key={p.id} className="p-6 bg-card border border-border rounded-xl shadow-sm hover:border-primary/30 transition-all cursor-pointer" onClick={() => setSelectedPosition(p)}>
                          <div className="flex justify-between items-start">
                             <div className="flex gap-6">
                                <div className={`w-1 h-12 rounded-full ${p.pnl >= 0 ? 'bg-success' : 'bg-danger'}`}></div>
                                <div>
                                   <div className="flex items-center gap-3 mb-1">
                                      <span className="font-black text-lg tracking-tight font-mono">{p.symbol}</span>
                                      <span className={`text-[9px] font-black uppercase px-2 py-0.5 rounded border ${p.pnl >= 0 ? 'bg-success/10 text-success border-success/20' : 'bg-danger/10 text-danger border-danger/20'}`}>{p.pnl >= 0 ? 'WIN' : 'LOSS'}</span>
                                   </div>
                                   <div className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider opacity-50">{p.created_at} • {p.side} {p.volume}L @ {p.entry_price.toFixed(5)}</div>
                                </div>
                             </div>
                             <div className="text-right flex flex-col items-end gap-2">
                                <div className={`text-2xl font-black font-mono ${p.pnl >= 0 ? 'text-success' : 'text-danger'}`}>
                                   {p.pnl >= 0 ? '+' : ''}${p.pnl.toFixed(2)}
                                </div>
                                <div className="flex gap-2">
                                  <Tags size={14} className="opacity-20"/><MessageSquare size={14} className="opacity-20"/>
                                </div>
                             </div>
                          </div>
                       </div>
                    ))}
                  </div>
               </Panel>
            )}

            {activeTab === 'brokers' && (
               <div className="space-y-6">
                  <Panel title="Broker Account Connectivity">
                     <div className="grid grid-cols-2 gap-8">
                        <div className="space-y-4">
                           {brokerAccounts.map(acc => (
                              <div key={acc.id} className="p-4 bg-secondary/10 border border-border rounded-lg flex justify-between items-center">
                                 <div>
                                    <div className="font-black uppercase tracking-tight">{acc.broker_name}</div>
                                    <div className="text-[10px] text-muted-foreground font-mono">ID: {acc.login} • Server: {acc.server}</div>
                                 </div>
                                 <div className="flex gap-2">
                                    <button onClick={() => axios.post(`${API_BASE}/brokers/test-connection/${acc.id}`).then(r => alert(JSON.stringify(r.data)))} className="bg-primary/10 text-primary border border-primary/20 px-3 py-1 rounded text-[10px] font-black uppercase">Test</button>
                                    <Badge status={acc.is_active ? 'live_ready' : 'used'}>{acc.is_active ? 'Active' : 'Disabled'}</Badge>
                                 </div>
                              </div>
                           ))}
                           <button className="w-full py-3 bg-secondary border border-dashed border-border rounded-lg text-[10px] font-black uppercase tracking-[0.2em] opacity-50 hover:opacity-100 transition-opacity">+ Add New Broker</button>
                        </div>
                        <div className="bg-secondary/5 border border-border rounded-xl p-6 space-y-4">
                            <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-primary mb-4">Link Exness MT5 Account</h4>
                            <div className="space-y-3">
                               <div>
                                  <label className="text-[9px] font-black text-muted-foreground uppercase mb-1 block">MT5 Login ID</label>
                                  <input className="w-full bg-background border border-border rounded px-4 py-2 text-xs font-mono" placeholder="e.g., 1234567"/>
                               </div>
                               <div>
                                  <label className="text-[9px] font-black text-muted-foreground uppercase mb-1 block">MT5 Password</label>
                                  <input type="password" className="w-full bg-background border border-border rounded px-4 py-2 text-xs" placeholder="••••••••"/>
                               </div>
                               <div>
                                  <label className="text-[9px] font-black text-muted-foreground uppercase mb-1 block">MT5 Server</label>
                                  <input className="w-full bg-background border border-border rounded px-4 py-2 text-xs font-mono" placeholder="Exness-MT5-Trial9"/>
                               </div>
                               <div className="pt-4">
                                  <button onClick={async () => {
                                      const login = (document.querySelector('input[placeholder="e.g., 1234567"]') as HTMLInputElement).value;
                                      const password = (document.querySelector('input[type="password"]') as HTMLInputElement).value;
                                      const server = (document.querySelector('input[placeholder="Exness-MT5-Trial9"]') as HTMLInputElement).value;
                                      await axios.post(`${API_BASE}/brokers/accounts`, {
                                          broker_name: 'Exness',
                                          login: parseInt(login),
                                          password: password,
                                          server: server,
                                          is_active: true
                                      });
                                      fetchData();
                                  }} className="w-full bg-primary py-3 rounded-lg font-black uppercase text-[11px] tracking-widest shadow-lg shadow-primary/20">Initialize Connection</button>
                               </div>
                            </div>
                        </div>
                     </div>
                  </Panel>
                  <Panel title="Exness API Health">
                      <div className="flex items-center gap-6 py-4">
                         <div className="flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-success"></div>
                            <span className="text-[10px] font-black uppercase tracking-widest">MT5 API Online</span>
                         </div>
                         <div className="flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-success"></div>
                            <span className="text-[10px] font-black uppercase tracking-widest">Terminal Synced</span>
                         </div>
                      </div>
                  </Panel>
               </div>
            )}

            {selectedPosition && (
               <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-8">
                 <div className="bg-card border border-border rounded-2xl w-full max-w-3xl shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
                    <div className="p-6 border-b border-border flex justify-between items-center bg-secondary/5">
                       <h2 className="font-black text-lg uppercase tracking-widest">Position Inspection: {selectedPosition.symbol}</h2>
                       <button onClick={() => setSelectedPosition(null)} className="text-muted-foreground hover:text-foreground font-black text-xl">×</button>
                    </div>
                    <div className="p-8 grid grid-cols-2 gap-8 overflow-y-auto max-h-[80vh]">
                       <div className="space-y-6">
                          <Panel title="Journal Reflection">
                             <div className="space-y-4">
                                <div>
                                   <label className="text-[9px] font-black text-muted-foreground uppercase mb-2 block tracking-widest">Operator Notes</label>
                                   <textarea className="w-full bg-background border border-border rounded-lg p-4 text-xs h-32 focus:border-primary outline-none transition-colors" placeholder="Describe setup context..."></textarea>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                   <div>
                                      <label className="text-[9px] font-black text-muted-foreground uppercase mb-2 block tracking-widest">Discipline</label>
                                      <div className="flex gap-1">
                                         {[1,2,3,4,5].map(s => <button key={s} className="flex-1 h-8 rounded bg-background border border-border text-[10px] font-black hover:border-primary transition-all">{s}</button>)}
                                      </div>
                                   </div>
                                   <div>
                                      <label className="text-[9px] font-black text-muted-foreground uppercase mb-2 block tracking-widest">Setup Quality</label>
                                      <div className="flex gap-1">
                                         {[1,2,3,4,5].map(s => <button key={s} className="flex-1 h-8 rounded bg-background border border-border text-[10px] font-black hover:border-primary transition-all">{s}</button>)}
                                      </div>
                                   </div>
                                </div>
                             </div>
                          </Panel>
                       </div>
                       <div className="space-y-6">
                          <Panel title="Live Target Ladder">
                             <div className="space-y-3">
                                {[
                                   { label: 'TP1 (0.5R)', price: selectedPosition.entry_price * 1.01, hit: true },
                                   { label: 'TP2 (1.0R)', price: selectedPosition.entry_price * 1.02, hit: false },
                                   { label: 'TP3 (2.0R)', price: selectedPosition.entry_price * 1.04, hit: false },
                                ].map((tp, idx) => (
                                   <div key={idx} className={`flex items-center justify-between p-3 rounded border ${tp.hit ? 'bg-success/5 border-success/30' : 'bg-background border-border'}`}>
                                      <div className="flex items-center gap-3">
                                         <div className={`w-2 h-2 rounded-full ${tp.hit ? 'bg-success' : 'bg-muted-foreground opacity-30'}`}></div>
                                         <span className="text-[10px] font-black uppercase">{tp.label}</span>
                                      </div>
                                      <span className="font-mono text-[10px] font-bold">{tp.price.toFixed(5)}</span>
                                   </div>
                                ))}
                                <div className="pt-2">
                                   <button className="w-full py-2 bg-secondary border border-border rounded text-[9px] font-black uppercase tracking-widest hover:border-primary transition-all">+ Add Scaling Target</button>
                                </div>
                             </div>
                          </Panel>
                          <div className="grid grid-cols-2 gap-4">
                             <button className="py-4 bg-danger/10 text-danger border border-danger/20 rounded-xl font-black uppercase text-[10px] tracking-widest hover:bg-danger hover:text-white transition-all shadow-lg shadow-danger/5">Panic Close</button>
                             <button onClick={() => setSelectedPosition(null)} className="py-4 bg-primary text-white rounded-xl font-black uppercase text-[10px] tracking-widest shadow-lg shadow-primary/20 hover:brightness-110 transition-all">Save Changes</button>
                          </div>
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

const Stat = ({ label, value, subtext, color = 'text-foreground' }: any) => (
  <div className="bg-card border border-border p-6 rounded-xl shadow-md border-b-4 border-b-primary/20">
    <div className="text-[10px] font-black text-muted-foreground uppercase tracking-[0.2em] mb-4 opacity-50">{label}</div>
    <div className={`text-3xl font-black tracking-tighter ${color}`}>{value}</div>
    {subtext && <div className="text-[10px] font-bold opacity-30 uppercase mt-2 tracking-widest">{subtext}</div>}
  </div>
);

const Panel = ({ title, children }: any) => (
  <div className="bg-card border border-border rounded-xl shadow-lg flex flex-col overflow-hidden">
    <div className="px-6 py-4 bg-secondary/5 border-b border-border flex items-center justify-between">
      <h3 className="text-xs font-black uppercase tracking-[0.15em] flex items-center gap-2"><TrendingUp size={14} className="text-primary"/> {title}</h3>
      <div className="w-2 h-2 rounded-full bg-primary/20 shadow-inner"></div>
    </div>
    <div className="p-6 flex-1">{children}</div>
  </div>
);

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

export default App;
