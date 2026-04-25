import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, Shield, Mail, Server, RefreshCw, AlertCircle, CheckCircle } from 'lucide-react';

const SystemHealth = () => {
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const checkHealth = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await axios.get('http://127.0.0.1:8000/api/health/full');
            setStatus(res.data);
        } catch (err) {
            setError("Failed to connect to backend server");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        checkHealth();
    }, []);

    const StatusCard = ({ title, icon: Icon, serviceKey }) => {
        if (!status) return null;
        const service = status[serviceKey];
        const isOk = service?.status === 'connected' || service?.status === 'OK';

        return (
            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700 shadow-lg flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-full ${isOk ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'}`}>
                        <Icon size={24} />
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold text-gray-200">{title}</h3>
                        <p className="text-sm text-gray-400">{service?.message || 'Unknown'}</p>
                    </div>
                </div>
                <div>
                    {isOk ? <CheckCircle className="text-green-500" /> : <AlertCircle className="text-red-500" />}
                </div>
            </div>
        );
    };

    return (
        <div className="p-8 max-w-4xl mx-auto">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                    <Activity className="text-blue-500" /> System Status
                </h1>
                <button
                    onClick={checkHealth}
                    disabled={loading}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-md transition disabled:opacity-50"
                >
                    <RefreshCw size={18} className={loading ? "animate-spin" : ""} />
                    Refresh
                </button>
            </div>

            {error && (
                <div className="bg-red-900/50 border border-red-700 text-red-200 p-4 rounded-md mb-6 flex items-center gap-2">
                    <AlertCircle size={20} />
                    {error}
                </div>
            )}

            {!status && !loading && !error && (
                <div className="text-center text-gray-500 mt-10">Press Refresh to check system status</div>
            )}

            {status && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <StatusCard title="VirusTotal API" icon={Shield} serviceKey="virustotal" />
                    <StatusCard title="DomainDuck API" icon={Server} serviceKey="domainduck" />
                    <StatusCard title="Local AI (Ollama)" icon={Activity} serviceKey="ollama" />
                    <StatusCard title="Gmail Integration" icon={Mail} serviceKey="gmail" />
                    <StatusCard title="Chrome Extension" icon={RefreshCw} serviceKey="extension" />

                </div>
            )}
        </div>
    );
};

export default SystemHealth;
