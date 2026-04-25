import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
    Mail, Globe, ShieldCheck, ShieldAlert, AlertTriangle,
    RefreshCw, ChevronDown, ChevronRight,
    ArrowDownRight, ExternalLink, Clock, Eye, Camera,
    Inbox, Bell, FileText, CheckCircle, X, Search
} from 'lucide-react';

/* ─── Color helpers ─── */
const statusColors = {
    safe: {
        bg: 'rgba(16, 185, 129, 0.08)',
        border: 'rgba(16, 185, 129, 0.25)',
        text: '#34d399',
        badge: 'bg-emerald-900/40 text-emerald-400 border-emerald-700/50',
    },
    unsafe: {
        bg: 'rgba(239, 68, 68, 0.08)',
        border: 'rgba(239, 68, 68, 0.25)',
        text: '#f87171',
        badge: 'bg-red-900/40 text-red-400 border-red-700/50',
    },
    error: {
        bg: 'rgba(234, 179, 8, 0.08)',
        border: 'rgba(234, 179, 8, 0.25)',
        text: '#fbbf24',
        badge: 'bg-yellow-900/40 text-yellow-400 border-yellow-700/50',
    },
    pending: {
        bg: 'rgba(107, 114, 128, 0.08)',
        border: 'rgba(107, 114, 128, 0.25)',
        text: '#9ca3af',
        badge: 'bg-gray-800 text-gray-400 border-gray-700',
    },
};

const getStatusTheme = (status) => statusColors[status] || statusColors.pending;

/* ─── Components ─── */

const HopNode = ({ hop, isLast, index, total }) => {
    const statusCode = hop.status || 0;
    const isRedirect = statusCode >= 300 && statusCode < 400;
    const isFinal = index === total - 1;
    const hasMalware = hop.cti_data?.verdict === 'Malicious';

    return (
        <div className="relative flex items-start gap-3 py-2 pl-8">
            {!isLast && (
                <div className="absolute left-3 top-8 bottom-0 w-px" style={{ background: 'rgba(100,116,139,0.3)' }} />
            )}
            <div className="absolute left-3 top-4 w-5 h-px" style={{ background: 'rgba(100,116,139,0.3)' }} />
            <div className={`relative z-10 w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0 border
                ${hasMalware ? 'bg-red-900/60 text-red-200 border-red-600' : isFinal ? 'bg-blue-900/60 text-blue-200 border-blue-600' : 'bg-gray-800 text-gray-400 border-gray-600'}`}>
                {hop.step + 1}
            </div>
            <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                    <span className={`font-mono text-sm break-all ${hasMalware ? 'text-red-400 font-bold' : isFinal ? 'text-blue-300' : 'text-gray-400'}`}>
                        {hop.url}
                    </span>
                    {statusCode > 0 && (
                        <span className={`text-xs px-1.5 py-0.5 rounded font-mono shrink-0 ${isRedirect ? 'bg-yellow-900/40 text-yellow-400' : statusCode >= 200 && statusCode < 300 ? 'bg-green-900/40 text-green-400' : 'bg-gray-700 text-gray-400'}`}>
                            {statusCode}
                        </span>
                    )}
                    {hasMalware && (
                        <span className="flex items-center gap-1 text-xs bg-red-900/50 text-red-300 px-2 py-0.5 rounded border border-red-800 shrink-0">
                            <AlertTriangle size={10} /> Malicious
                        </span>
                    )}
                </div>
            </div>
        </div>
    );
};

const UrlBranch = ({ urlObj, index, isLast, onAnalyze }) => {
    const [expanded, setExpanded] = useState(false);
    const theme = getStatusTheme(urlObj.status);
    const chain = urlObj.full_analysis?.chain || [];
    const summary = urlObj.full_analysis?.summary_report || urlObj.explanation;

    return (
        <div className="relative">
            {!isLast && <div className="absolute left-5 top-12 bottom-0 w-px" style={{ background: 'rgba(59,130,246,0.15)' }} />}
            <div className="absolute left-0 top-5 w-5 h-px" style={{ background: 'rgba(59,130,246,0.3)' }} />
            <div className="ml-6">
                <div className="group cursor-pointer rounded-lg border p-3 transition-all hover:shadow-lg hover:shadow-black/20"
                    style={{ background: theme.bg, borderColor: theme.border }} onClick={() => setExpanded(!expanded)}>
                    <div className="flex items-center gap-3">
                        <div className="shrink-0">
                            {urlObj.status === 'unsafe' ? <ShieldAlert size={18} style={{ color: theme.text }} /> :
                                urlObj.status === 'safe' ? <ShieldCheck size={18} style={{ color: theme.text }} /> :
                                    <Globe size={18} style={{ color: theme.text }} />}
                        </div>
                        <div className="flex-1 min-w-0">
                            <div className="font-mono text-sm break-all" style={{ color: theme.text }}>{urlObj.url}</div>
                            <div className="text-xs text-gray-500 mt-1 line-clamp-1">{urlObj.explanation}</div>
                        </div>
                        <div className="flex items-center gap-2 shrink-0">
                            <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase border ${theme.badge}`}>{urlObj.status}</span>
                            <div className="text-gray-500">{chain.length > 0 && (expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />)}</div>
                        </div>
                    </div>
                </div>
                {expanded && (
                    <div className="mt-2 ml-4 border-l-2 border-gray-800 pl-4 pb-2">
                        {chain.length > 0 && (
                            <div className="mb-4">
                                <div className="text-xs text-gray-500 uppercase tracking-widest mb-2 flex items-center gap-1"><ArrowDownRight size={12} /> Redirection Chain ({chain.length} hops)</div>
                                <div className="space-y-0">
                                    {chain.map((hop, i) => <HopNode key={i} hop={hop} index={i} total={chain.length} isLast={i === chain.length - 1} />)}
                                </div>
                            </div>
                        )}
                        {summary && (
                            <div className="bg-gray-900/80 border border-gray-800 rounded-lg p-4 mt-3">
                                <div className="text-xs text-gray-500 uppercase tracking-widest mb-2 flex items-center gap-1"><Eye size={12} /> AI Analysis Summary</div>
                                <div className="text-sm text-gray-300 whitespace-pre-wrap leading-relaxed font-mono">{summary}</div>
                            </div>
                        )}
                        {urlObj.full_analysis && onAnalyze && (
                            <button onClick={(e) => { e.stopPropagation(); onAnalyze(urlObj.full_analysis); }}
                                className="mt-4 flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white text-sm font-semibold rounded-lg transition-all shadow-lg shadow-blue-900/30">
                                <ExternalLink size={14} /> Deep Analysis — Open in Redirection Detective
                            </button>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

// Auth Badge Component
const AuthBadge = ({ type, status }) => {
    const isPass = status === 'pass';
    const isFail = status === 'fail' || status === 'softfail';
    const isNeutral = !status || status === 'none' || status === 'neutral';

    let colorClass = 'bg-gray-800 text-gray-500 border-gray-700';
    if (isPass) colorClass = 'bg-emerald-900/30 text-emerald-400 border-emerald-800/50';
    if (isFail) colorClass = 'bg-red-900/30 text-red-400 border-red-800/50';

    return (
        <span className={`px-1.5 py-0.5 rounded-[4px] text-[9px] font-bold border uppercase tracking-tighter ${colorClass}`} title={`${type}: ${status || 'unknown'}`}>
            {type}
        </span>
    );
};

// Table Header Component
const EmailTableHeader = () => (
    <div className="grid grid-cols-12 gap-4 px-4 py-3 text-xs font-bold text-gray-500 uppercase tracking-widest border-b border-gray-800 bg-gray-900/50 rounded-t-lg">
        <div className="col-span-1 text-center">Severity</div>
        <div className="col-span-3">Account</div>
        <div className="col-span-3">Subject</div>
        <div className="col-span-2">From</div>
        <div className="col-span-1">Date</div>
        <div className="col-span-2 text-right">Status / Action</div>
    </div>
);

// Unified Table Row Component
const EmailTableRow = ({ email, onAnalyze, onResolve, viewMode }) => {
    const [expanded, setExpanded] = useState(false);
    const theme = getStatusTheme(email.overall_verdict);
    const dateStr = email.date ? new Date(email.date).toLocaleDateString() : '-';

    return (
        <div className="border-b border-gray-800 last:border-0 bg-gray-900/30 hover:bg-gray-800/50 transition-colors">
            <div
                onClick={() => setExpanded(!expanded)}
                className="grid grid-cols-12 gap-4 items-center p-4 cursor-pointer text-sm"
            >
                <div className="col-span-1 flex justify-center">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${theme.badge}`}>
                        {email.overall_verdict === 'unsafe' ? <ShieldAlert size={14} /> : <ShieldCheck size={14} />}
                    </div>
                </div>
                <div className="col-span-3 text-gray-300 truncate text-xs font-mono" title={email.account}>
                    {email.account || 'Unknown'}
                </div>
                <div className="col-span-3 font-semibold text-white truncate pr-2" title={email.subject}>
                    {email.subject || '(No Subject)'}
                </div>
                <div className="col-span-2 text-gray-400 truncate pr-2">
                    <div className="truncate" title={email.from}>{email.from}</div>
                    <div className="flex gap-1 mt-1">
                        <AuthBadge type="SPF" status={email.auth_results?.spf} />
                        <AuthBadge type="DKIM" status={email.auth_results?.dkim} />
                        <AuthBadge type="DMRC" status={email.auth_results?.dmarc} />
                    </div>
                </div>
                <div className="col-span-1 text-gray-500 text-xs flex items-center gap-1">
                    <Clock size={12} /> {dateStr}
                </div>
                <div className="col-span-2 flex items-center justify-end gap-2">
                    {viewMode === 'alerts' ? (
                        <button
                            onClick={(e) => { e.stopPropagation(); onResolve(email); }}
                            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded flex items-center gap-1 transition-all shadow-lg shadow-blue-900/20"
                        >
                            <CheckCircle size={12} /> Resolve
                        </button>
                    ) : (
                        <span className={`px-2 py-0.5 rounded text-[10px] uppercase border ${theme.badge} font-bold`}>
                            {email.status === 'Resolved' ? 'Resolved' : email.overall_verdict}
                        </span>
                    )}
                    <div className="text-gray-600 ml-1">
                        {expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                    </div>
                </div>
            </div>

            {expanded && (
                <div className="bg-gray-900/80 p-6 pl-16 border-t border-gray-800 shadow-inner">
                    {email.closure_notes && (
                        <div className="mb-4 p-3 bg-gray-800/50 border border-gray-700 rounded-lg text-sm">
                            <span className="text-gray-400 font-bold uppercase text-xs block mb-1">Details & Notes</span>
                            <p className="text-gray-300">{email.closure_notes}</p>
                        </div>
                    )}

                    {email.auth_results?.raw && (
                        <div className="mb-4 p-3 bg-gray-900/50 border border-gray-800 rounded-lg text-[10px] font-mono">
                            <span className="text-gray-500 font-bold uppercase text-[9px] block mb-1">Raw Authentication Results</span>
                            <div className="text-gray-400 break-all">{email.auth_results.raw}</div>
                        </div>
                    )}

                    <div className="mb-2 text-xs font-bold text-gray-500 uppercase tracking-widest flex items-center gap-2">
                        <Globe size={12} /> Extracted URLs ({email.urls?.length || 0})
                    </div>

                    {email.urls && email.urls.length > 0 ? (
                        <div className="space-y-3">
                            {email.urls.map((urlObj, idx) => (
                                <UrlBranch key={idx} urlObj={urlObj} index={idx} isLast={idx === email.urls.length - 1} onAnalyze={onAnalyze} />
                            ))}
                        </div>
                    ) : (
                        <div className="text-gray-500 text-sm italic py-2">No URLs found in this email.</div>
                    )}

                    {email.tracking_pixels && email.tracking_pixels.length > 0 && (
                        <div className="mt-6">
                            <div className="mb-2 text-xs font-bold text-gray-500 uppercase tracking-widest flex items-center gap-2">
                                <Camera size={12} /> Tracking Pixels Detected ({email.tracking_pixels.length})
                            </div>
                            <div className="space-y-2">
                                {email.tracking_pixels.map((pixel, idx) => (
                                    <div key={idx} className="bg-gray-800/40 border border-gray-700/50 rounded-lg p-3">
                                        <div className="flex items-center gap-2 mb-1">
                                            <div className="w-1.5 h-1.5 rounded-full bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]"></div>
                                            <span className="text-[10px] text-amber-500 font-bold uppercase">Pixel Found</span>
                                        </div>
                                        <div className="text-[11px] text-gray-300 break-all font-mono opacity-80 mb-1">
                                            {pixel.url}
                                        </div>
                                        <div className="flex flex-wrap gap-2">
                                            {pixel.reasons.map((reason, ridx) => (
                                                <span key={ridx} className="bg-amber-900/20 text-amber-400/70 border border-amber-800/30 px-1.5 py-0.5 rounded text-[9px] font-medium">
                                                    {reason}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};


/* ─── Resolution Modal ─── */
const ResolutionModal = ({ isOpen, onClose, onConfirm, email }) => {
    const [notes, setNotes] = useState('');
    const [status, setStatus] = useState('Resolved');

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 backdrop-blur-sm">
            <div className="bg-gray-900 border border-gray-700 rounded-xl w-full max-w-md p-6 shadow-2xl">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xl font-bold text-white flex items-center gap-2"><CheckCircle className="text-blue-500" /> Resolve Alert</h3>
                    <button onClick={onClose} className="text-gray-500 hover:text-white"><X size={20} /></button>
                </div>

                <div className="mb-4 text-sm text-gray-400">
                    Resolving offense for: <span className="text-white font-mono">{email?.subject}</span>
                </div>

                <div className="space-y-4">
                    <div>
                        <label className="block text-xs font-semibold text-gray-500 uppercase mb-1">Status</label>
                        <select
                            value={status}
                            onChange={(e) => setStatus(e.target.value)}
                            className="w-full bg-gray-800 border border-gray-700 text-white rounded p-2 focus:border-blue-500 outline-none"
                        >
                            <option value="Resolved">Resolved (Fixed)</option>
                            <option value="False Positive">False Positive</option>
                            <option value="Ignored">Ignored / Acceptable Risk</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-xs font-semibold text-gray-500 uppercase mb-1">Closure Notes</label>
                        <textarea
                            value={notes}
                            onChange={(e) => setNotes(e.target.value)}
                            className="w-full bg-gray-800 border border-gray-700 text-white rounded p-2 h-24 focus:border-blue-500 outline-none resize-none"
                            placeholder="e.g. User confirms legitimate sender..."
                        />
                    </div>
                </div>

                <div className="flex justify-end gap-3 mt-6">
                    <button onClick={onClose} className="px-4 py-2 text-gray-400 hover:text-white transition-colors">Cancel</button>
                    <button
                        onClick={() => onConfirm(status, notes)}
                        disabled={!notes.trim()}
                        className="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Confirm Resolution
                    </button>
                </div>
            </div>
        </div>
    );
};

/* ─── Main Component ─── */
const EmailScan = ({ onAnalyze }) => {
    const [emails, setEmails] = useState([]);
    const [loading, setLoading] = useState(false);
    const [scanning, setScanning] = useState(false);
    const [activeView, setActiveView] = useState('alerts'); // 'alerts' | 'history'
    const [searchQuery, setSearchQuery] = useState('');

    // Resolution state
    const [resolveModalOpen, setResolveModalOpen] = useState(false);
    const [selectedEmail, setSelectedEmail] = useState(null);

    // Connection Status
    const [connectionStatus, setConnectionStatus] = useState({ connected: false, email: null, loading: true });
    const [accounts, setAccounts] = useState([]);
    const [accountsExpanded, setAccountsExpanded] = useState(false);

    const checkStatus = async () => {
        try {
            const res = await axios.get('http://127.0.0.1:8000/api/gmail/status');
            setConnectionStatus({ connected: res.data.connected, email: res.data.email, loading: false });
        } catch (err) {
            setConnectionStatus({ connected: false, email: null, loading: false, error: true });
        }
    };

    const fetchAccounts = async () => {
        try {
            const res = await axios.get('http://127.0.0.1:8000/api/gmail/accounts');
            setAccounts(res.data);
        } catch (err) {
            console.error('Failed to fetch accounts:', err);
        }
    };

    const fetchResults = async () => {
        setLoading(true);
        try {
            const res = await axios.get('http://127.0.0.1:8000/api/gmail/results');
            setEmails(res.data);
            // Auto-switch to history if alerts are empty but history has data (UX improvement)
            // But only on initial load to avoid jumping while user is interacting
            // if (res.data.length > 0 && res.data.filter(e => e.status === 'Open').length === 0) {
            //     setActiveView('history');
            // }
        } catch (err) {
            console.error('Failed to fetch results:', err);
        } finally {
            setLoading(false);
        }
    };

    const triggerScan = async () => {
        setScanning(true);
        try {
            await axios.post('http://127.0.0.1:8000/api/gmail/scan');
            setTimeout(fetchResults, 5000);
            checkStatus(); // Recheck status
        } catch (err) {
            alert("Scan trigger failed: " + err.message);
        } finally {
            setScanning(false);
        }
    };

    useEffect(() => {
        checkStatus();
        fetchResults();
        fetchAccounts();
        const interval = setInterval(() => {
            fetchResults();
            checkStatus();
            fetchAccounts();
        }, 30000);
        return () => clearInterval(interval);
    }, []);

    const openResolveModal = (email) => {
        setSelectedEmail(email);
        setResolveModalOpen(true);
    };

    const handleResolve = async (status, notes) => {
        if (!selectedEmail) return;
        try {
            await axios.post(`http://127.0.0.1:8000/api/gmail/resolve/${selectedEmail.email_id}`, {
                status,
                closure_notes: notes
            });
            // Update local state optimistic
            setEmails(emails.map(e => e.email_id === selectedEmail.email_id ? { ...e, status, closure_notes: notes } : e));
            setResolveModalOpen(false);
            setSelectedEmail(null);
        } catch (err) {
            alert("Failed to resolve: " + err.message);
        }
    };

    // Derived State
    const alerts = emails.filter(e => e.status === 'Open' && e.overall_verdict !== 'safe' && e.overall_verdict !== 'Clean');
    const filteredEmails = emails.filter(e => {
        if (!searchQuery) return true;
        const q = searchQuery.toLowerCase();
        return (e.subject?.toLowerCase().includes(q) || e.from?.toLowerCase().includes(q));
    });

    const displayEmails = activeView === 'alerts' ? alerts : filteredEmails;

    return (
        <div className="flex h-[calc(100vh-100px)]">
            {/* Sidebar */}
            <div className="w-64 bg-gray-900 border-r border-gray-800 p-4 flex flex-col gap-2">
                <button
                    onClick={() => setActiveView('alerts')}
                    className={`flex items-center justify-between px-4 py-3 rounded-lg font-semibold transition-colors ${activeView === 'alerts' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-gray-800'}`}
                >
                    <div className="flex items-center gap-3">
                        <Bell size={18} /> Alerts
                    </div>
                    {alerts.length > 0 && (
                        <span className="bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">{alerts.length}</span>
                    )}
                </button>
                <button
                    onClick={() => setActiveView('history')}
                    className={`flex items-center justify-between px-4 py-3 rounded-lg font-semibold transition-colors ${activeView === 'history' ? 'bg-gray-800 text-white' : 'text-gray-400 hover:bg-gray-800'}`}
                >
                    <div className="flex items-center gap-3">
                        <Inbox size={18} /> All Emails
                    </div>
                    <span className="text-gray-600 text-xs">{emails.length}</span>
                </button>

                <div className="mt-auto pt-4 border-t border-gray-800">
                    {/* Integration Status Panel */}
                    <div className="mb-3 px-2">
                        <button
                            onClick={() => { setAccountsExpanded(!accountsExpanded); fetchAccounts(); }}
                            className="w-full flex items-center justify-between group"
                        >
                            <div className="text-xs font-semibold text-gray-500 uppercase tracking-widest">Integration Status</div>
                            <div className="flex items-center gap-1.5">
                                {accounts.filter(a => a.is_connected).length > 0 && (
                                    <span className="text-[10px] bg-emerald-900/50 text-emerald-400 border border-emerald-700/50 px-1.5 py-0.5 rounded-full font-bold">
                                        {accounts.filter(a => a.is_connected).length} connected
                                    </span>
                                )}
                                <span className="text-gray-600 text-xs">{accountsExpanded ? '▲' : '▼'}</span>
                            </div>
                        </button>

                        {/* Quick status line */}
                        <div className="mt-1.5">
                            {connectionStatus.loading ? (
                                <div className="text-gray-500 text-xs flex items-center gap-2"><RefreshCw size={10} className="animate-spin" /> Checking...</div>
                            ) : connectionStatus.connected ? (
                                <div className="flex items-center gap-2 text-green-400 text-xs">
                                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                                    <span className="truncate">{connectionStatus.email || 'Active'}</span>
                                </div>
                            ) : (
                                <div className="flex items-center gap-2 text-red-400 text-xs">
                                    <div className="w-2 h-2 rounded-full bg-red-500"></div>
                                    <span>Disconnected</span>
                                </div>
                            )}
                        </div>

                        {/* Expanded account list */}
                        {accountsExpanded && (
                            <div className="mt-3 space-y-2">
                                {accounts.length === 0 ? (
                                    <div className="text-xs text-gray-600 italic">No accounts registered yet.</div>
                                ) : (
                                    accounts.map((acc) => (
                                        <div key={acc.email} className={`rounded-lg border px-3 py-2 ${acc.is_connected
                                            ? 'bg-emerald-900/10 border-emerald-800/40'
                                            : 'bg-gray-800/40 border-gray-700/50'
                                            }`}>
                                            <div className="flex items-center gap-2">
                                                <div className={`w-2 h-2 rounded-full shrink-0 ${acc.is_connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                                                    }`} />
                                                <span className={`text-xs font-mono truncate ${acc.is_connected ? 'text-green-300' : 'text-gray-400'
                                                    }`} title={acc.email}>
                                                    {acc.email}
                                                </span>
                                            </div>
                                            <div className="mt-1 text-[10px] text-gray-600 pl-4">
                                                {acc.is_connected ? (
                                                    <span className="text-emerald-600">● Connected</span>
                                                ) : (
                                                    <span className="text-red-700">● Disconnected</span>
                                                )}
                                                {acc.last_seen && (
                                                    <span className="ml-2">· Last seen {new Date(acc.last_seen).toLocaleDateString()}</span>
                                                )}
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        )}

                        {!connectionStatus.loading && !connectionStatus.connected && (
                            <div className="text-[10px] text-gray-600 mt-1 leading-tight">
                                Backend cannot access Gmail API. Check logs or re-authenticate.
                            </div>
                        )}
                    </div>

                    <button onClick={triggerScan} disabled={scanning} className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg text-sm border border-gray-700 transition-colors">
                        <RefreshCw size={14} className={scanning ? 'animate-spin' : ''} />
                        {scanning ? 'Scanning...' : 'Scan Now'}
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 overflow-y-auto p-8 relative">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                            {activeView === 'alerts' ? <AlertTriangle className="text-red-500" /> : <FileText className="text-blue-400" />}
                            {activeView === 'alerts' ? 'Active Threats' : 'Email Security History'}
                        </h2>
                        <p className="text-gray-500 text-sm mt-1">
                            {activeView === 'alerts' ? 'Investigate and resolve open security alerts.' : 'Complete audit log of all scanned emails.'}
                        </p>
                    </div>

                    {activeView === 'history' && (
                        <div className="relative">
                            <Search className="absolute left-3 top-2.5 text-gray-500" size={16} />
                            <input
                                type="text"
                                placeholder="Search emails..."
                                className="bg-gray-800 border border-gray-700 text-white text-sm rounded-lg pl-9 pr-4 py-2 focus:ring-2 focus:ring-blue-500 outline-none w-64"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                        </div>
                    )}
                </div>

                {loading && emails.length === 0 ? (
                    <div className="text-center py-20 text-gray-500 flex flex-col items-center">
                        <RefreshCw className="animate-spin mb-4" /> Loading threats...
                    </div>
                ) : (
                    <div>
                        {displayEmails.length === 0 ? (
                            <div className="text-center py-20 border border-gray-800 rounded-xl bg-gray-900/30">
                                <div className="text-gray-500 mb-2">No {activeView === 'alerts' ? 'active alerts' : 'emails found'}.</div>
                                {activeView === 'alerts' ? <CheckCircle className="mx-auto text-green-500/50" /> : <Inbox className="mx-auto text-gray-600" />}
                            </div>
                        ) : (
                            <div className="bg-gray-900/30 border border-gray-800 rounded-lg overflow-hidden">
                                <EmailTableHeader />
                                {displayEmails.map((email, idx) => (
                                    <EmailTableRow
                                        key={email.email_id || idx}
                                        email={email}
                                        onAnalyze={onAnalyze}
                                        onResolve={openResolveModal}
                                        viewMode={activeView}
                                    />
                                ))}
                            </div>
                        )}
                        {displayEmails.length > 0 && activeView === 'history' && (
                            <div className="text-center text-xs text-gray-600 mt-4">End of history.</div>
                        )}
                    </div>
                )}
            </div>

            <ResolutionModal
                isOpen={resolveModalOpen}
                onClose={() => setResolveModalOpen(false)}
                onConfirm={handleResolve}
                email={selectedEmail}
            />
        </div>
    );
};

export default EmailScan;
