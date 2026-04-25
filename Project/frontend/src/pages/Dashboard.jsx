import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Shield, ArrowRight, Loader2, AlertTriangle, Clock, Trash2, RotateCcw } from 'lucide-react';
import RedirectionChain from '../components/RedirectionChain';

const Dashboard = ({ initialData }) => {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [report, setReport] = useState(null);
    const [error, setError] = useState('');
    const [activeTab, setActiveTab] = useState('analyze');
    const [history, setHistory] = useState([]);
    const [historyLoading, setHistoryLoading] = useState(false);

    // Initial data from Email Scan or other sources
    useEffect(() => {
        if (initialData) {
            setReport(initialData);
            setUrl(initialData.original_url || '');
            setActiveTab('analyze');
        }
    }, [initialData]);

    // Fetch history on mount
    useEffect(() => {
        fetchHistory();
    }, []);

    const fetchHistory = async () => {
        setHistoryLoading(true);
        try {
            const res = await axios.get('http://127.0.0.1:8000/api/history?limit=100');
            setHistory(res.data);
        } catch (err) {
            console.error('Failed to load history:', err);
        } finally {
            setHistoryLoading(false);
        }
    };

    const deleteHistoryEntry = async (id, e) => {
        e.stopPropagation();
        try {
            await axios.delete(`http://127.0.0.1:8000/api/history/${id}`);
            // Optimistic update
            setHistory(history.filter(h => h.id !== id));
        } catch (err) {
            console.error('Failed to delete entry:', err);
            alert('Failed to delete entry');
        }
    };

    const clearHistory = async () => {
        if (!confirm('Are you sure you want to clear all history?')) return;
        try {
            await axios.delete('http://127.0.0.1:8000/api/history');
            setHistory([]);
        } catch (err) {
            console.error('Failed to clear history:', err);
            alert('Failed to clear history');
        }
    };

    const handleAnalyze = async (e) => {
        e.preventDefault();
        if (!url) return;

        setLoading(true);
        setError('');
        setReport(null);

        try {
            const response = await axios.post('http://127.0.0.1:8000/api/analyze', { url });
            setReport(response.data);
            // Refresh history to show the new scan
            fetchHistory();
        } catch (err) {
            setError('Failed to analyze URL. ' + (err.response?.data?.detail || err.message));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container mx-auto p-6 max-w-6xl">
            <div className="flex items-center gap-3 mb-8">
                <Shield className="w-10 h-10 text-emerald-400" />
                <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-blue-500">
                    Redirection Detective
                </h1>
            </div>

            {/* Tabs */}
            <div className="flex gap-2 mb-6">
                <button
                    onClick={() => setActiveTab('analyze')}
                    className={`px-6 py-2 rounded-lg font-semibold transition-colors ${activeTab === 'analyze'
                        ? 'bg-emerald-600 text-white'
                        : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                        }`}
                >
                    Analyze
                </button>
                <button
                    onClick={() => {
                        setActiveTab('history');
                        fetchHistory();
                    }}
                    className={`px-6 py-2 rounded-lg font-semibold transition-colors flex items-center gap-2 ${activeTab === 'history'
                        ? 'bg-emerald-600 text-white'
                        : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                        }`}
                >
                    <Clock className="w-4 h-4" />
                    History ({history.length})
                </button>
            </div>

            {activeTab === 'analyze' && (
                <>
                    {/* Input Section */}
                    <div className="bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-700 mb-8">
                        <form onSubmit={handleAnalyze} className="flex gap-4">
                            <input
                                type="url"
                                placeholder="Enter suspicious URL (e.g., http://bit.ly/...)"
                                className="flex-1 bg-gray-900 border border-gray-600 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none transition-all"
                                value={url}
                                onChange={(e) => setUrl(e.target.value)}
                                required
                            />
                            <button
                                type="submit"
                                disabled={loading}
                                className="bg-emerald-600 hover:bg-emerald-700 text-white px-8 py-3 rounded-lg font-semibold flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {loading ? <Loader2 className="animate-spin" /> : 'Analyze'}
                            </button>
                        </form>
                        {error && (
                            <div className="mt-4 p-4 bg-red-900/30 border border-red-800 text-red-200 rounded-lg flex items-center gap-2">
                                <AlertTriangle className="w-5 h-5" />
                                {error}
                            </div>
                        )}
                    </div>

                    {/* Results Section */}
                    {report && (
                        <div className="bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-700">
                            <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                                <ArrowRight className="text-purple-400" />
                                Redirection Chain
                            </h2>
                            <RedirectionChain chain={report.chain} summaryReport={report.summary_report} />
                        </div>
                    )}
                </>
            )}

            {activeTab === 'history' && (
                <div className="bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-700">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-xl font-semibold flex items-center gap-2">
                            Analysis History
                            {historyLoading && <Loader2 className="w-4 h-4 animate-spin text-gray-500" />}
                        </h2>
                        <div className="flex gap-2">
                            <button
                                onClick={fetchHistory}
                                className="p-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors"
                                title="Refresh"
                            >
                                <RotateCcw className="w-4 h-4" />
                            </button>
                            <button
                                onClick={clearHistory}
                                className="flex items-center gap-2 px-4 py-2 bg-red-900/30 border border-red-800 text-red-300 rounded-lg hover:bg-red-900/50 transition-colors"
                            >
                                <Trash2 className="w-4 h-4" />
                                Clear History
                            </button>
                        </div>
                    </div>
                    <div className="space-y-3">
                        {history.length === 0 && !historyLoading ? (
                            <div className="text-center py-12 text-gray-500">
                                <Clock className="w-12 h-12 mx-auto mb-3 opacity-20" />
                                <p>No analysis history found.</p>
                                <p className="text-sm mt-1">Scans will be saved here automatically.</p>
                            </div>
                        ) : (
                            history.map((entry) => (
                                <div
                                    key={entry.id}
                                    className="bg-gray-900 p-4 rounded-lg border border-gray-700 hover:border-emerald-500 transition-colors"
                                >
                                    <div className="flex justify-between items-start gap-3">
                                        <div
                                            className="flex-1 min-w-0 cursor-pointer group"
                                            onClick={() => {
                                                setReport(entry.report);
                                                setActiveTab('analyze');
                                            }}
                                        >
                                            <div className="flex items-center gap-2 mb-1">
                                                <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase 
                                                    ${entry.verdict === 'Malicious' ? 'bg-red-900/50 text-red-400 border border-red-800' :
                                                        entry.verdict === 'Suspicious' ? 'bg-yellow-900/50 text-yellow-400 border border-yellow-800' :
                                                            'bg-emerald-900/30 text-emerald-400 border border-emerald-800'
                                                    }`}
                                                >
                                                    {entry.verdict || 'Clean'}
                                                </span>
                                                <span className="text-gray-500 text-xs">
                                                    {new Date(entry.timestamp).toLocaleString()}
                                                </span>
                                            </div>
                                            <p className="text-blue-300 font-mono text-sm truncate group-hover:text-blue-200 transition-colors">
                                                {entry.url}
                                            </p>
                                        </div>
                                        <div className="flex items-center gap-3">
                                            <div className="text-right hidden sm:block">
                                                <div className="text-xs text-gray-500">Risk Score</div>
                                                <div className={`font-bold ${entry.risk_score > 50 ? 'text-red-400' : 'text-gray-400'}`}>
                                                    {entry.risk_score}/100
                                                </div>
                                            </div>
                                            <button
                                                onClick={(e) => deleteHistoryEntry(entry.id, e)}
                                                className="p-2 bg-red-900/20 border border-red-900/50 text-red-400/70 rounded hover:bg-red-900/40 hover:text-red-300 transition-colors"
                                                title="Delete this entry"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default Dashboard;
