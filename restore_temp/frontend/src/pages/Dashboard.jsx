import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Shield, ArrowRight, Loader2, AlertTriangle, Clock, Trash2 } from 'lucide-react';
import RedirectionChain from '../components/RedirectionChain';

const Dashboard = () => {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [report, setReport] = useState(null);
    const [error, setError] = useState('');
    const [activeTab, setActiveTab] = useState('analyze');
    const [history, setHistory] = useState([]);

    useEffect(() => {
        const savedHistory = localStorage.getItem('urlAnalysisHistory');
        if (savedHistory) {
            setHistory(JSON.parse(savedHistory));
        }
    }, []);

    const saveToHistory = (analysisData) => {
        // Create lightweight version without screenshots and HTML content
        const lightweightChain = analysisData.chain.map(node => ({
            step: node.step,
            url: node.url,
            status: node.status,
            cti_data: node.cti_data,
            // Exclude: screenshot, body_summary, extracted_links to save space
        }));

        const historyEntry = {
            url: analysisData.original_url,
            timestamp: new Date().toISOString(),
            report: {
                original_url: analysisData.original_url,
                chain: lightweightChain,
                summary_report: analysisData.summary_report?.substring(0, 200) + '...' // Truncate summary
            }
        };

        try {
            const newHistory = [historyEntry, ...history].slice(0, 20); // Reduced from 50 to 20
            setHistory(newHistory);
            localStorage.setItem('urlAnalysisHistory', JSON.stringify(newHistory));
        } catch (e) {
            console.error('Failed to save history:', e);
            // If still fails, clear old history
            localStorage.removeItem('urlAnalysisHistory');
            setHistory([historyEntry]);
            localStorage.setItem('urlAnalysisHistory', JSON.stringify([historyEntry]));
        }
    };

    const clearHistory = () => {
        setHistory([]);
        localStorage.removeItem('urlAnalysisHistory');
    };

    const handleAnalyze = async (e) => {
        e.preventDefault();
        if (!url) return;

        setLoading(true);
        setError('');
        setReport(null);

        try {
            const response = await axios.post('http://localhost:8000/api/analyze', { url });
            setReport(response.data);
            saveToHistory(response.data);
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
                    onClick={() => setActiveTab('history')}
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
                        <h2 className="text-xl font-semibold">Analysis History</h2>
                        <button
                            onClick={clearHistory}
                            className="flex items-center gap-2 px-4 py-2 bg-red-900/30 border border-red-800 text-red-300 rounded-lg hover:bg-red-900/50 transition-colors"
                        >
                            <Trash2 className="w-4 h-4" />
                            Clear History
                        </button>
                    </div>
                    <div className="space-y-3">
                        {history.length === 0 ? (
                            <p className="text-gray-400 text-center py-8">No analysis history yet</p>
                        ) : (
                            history.map((entry, idx) => (
                                <div
                                    key={idx}
                                    onClick={() => {
                                        setReport(entry.report);
                                        setActiveTab('analyze');
                                    }}
                                    className="bg-gray-900 p-4 rounded-lg border border-gray-700 hover:border-emerald-500 cursor-pointer transition-colors"
                                >
                                    <div className="flex justify-between items-start">
                                        <div className="flex-1 min-w-0">
                                            <p className="text-blue-300 font-mono text-sm truncate">{entry.url}</p>
                                            <p className="text-gray-500 text-xs mt-1">
                                                {new Date(entry.timestamp).toLocaleString()}
                                            </p>
                                        </div>
                                        <span className="text-xs px-2 py-1 bg-gray-800 text-gray-400 rounded ml-2">
                                            {entry.report.chain?.length || 0} hops
                                        </span>
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
