import React, { useState } from 'react';
import { ExternalLink, Camera, FileText, Clock, X, Maximize2, Code, ChevronDown, ChevronUp } from 'lucide-react';

const RedirectionChain = ({ chain, summaryReport }) => {
    const [selectedNode, setSelectedNode] = useState(null);
    const [fullscreenImage, setFullscreenImage] = useState(null);
    const [expandedBodyStep, setExpandedBodyStep] = useState(null);

    // Custom formatter to handle the AI report markdown without external libraries
    // This prevents the "Block Page" crash caused by react-markdown
    const renderSummary = (text) => {
        if (!text) return null;

        // Split by lines
        const lines = text.split('\n');

        return lines.map((line, i) => {
            // Handle Headers (## Title)
            if (line.trim().startsWith('##')) {
                return (
                    <h2 key={i} className="text-blue-300 font-bold mt-3 mb-1 text-xs uppercase tracking-wider">
                        {line.replace(/^##\s*/, '')}
                    </h2>
                );
            }
            // Handle List Items (- Item)
            if (line.trim().startsWith('- ')) {
                // Parse bolding within list item (**text**)
                const content = line.trim().substring(2);
                return (
                    <li key={i} className="text-gray-300 list-disc list-inside ml-2">
                        {parseBold(content)}
                    </li>
                );
            }
            // Handle Empty lines
            if (!line.trim()) {
                return <div key={i} className="h-2"></div>;
            }
            // Normal paragraphs
            return (
                <p key={i} className="mb-1 text-gray-300">
                    {parseBold(line)}
                </p>
            );
        });
    };

    // Helper to parse **bold** text
    const parseBold = (text) => {
        const parts = text.split(/(\*\*.*?\*\*)/g);
        return parts.map((part, index) => {
            if (part.startsWith('**') && part.endsWith('**')) {
                return <strong key={index} className="text-white font-semibold">{part.slice(2, -2)}</strong>;
            }
            return part;
        });
    };

    return (
        <div className="space-y-4">
            <div className="relative border-l-2 border-gray-700 ml-4 space-y-8 py-2">
                {chain.map((node, index) => {
                    const verdict = node.cti_data?.verdict?.toLowerCase() || '';
                    const isMalicious = verdict === 'malicious';
                    const isSuspicious = verdict === 'suspicious';
                    const isBodyExpanded = expandedBodyStep === index;

                    let statusColor = 'bg-emerald-500 border-emerald-900'; // Default safe
                    if (isMalicious) statusColor = 'bg-red-500 border-red-900';
                    if (isSuspicious) statusColor = 'bg-orange-500 border-orange-900';

                    return (
                        <div key={index} className="relative pl-8">
                            {/* Dot on the timeline */}
                            <div
                                className={`absolute -left-[9px] top-4 w-4 h-4 rounded-full border-2 ${statusColor}`}
                            />

                            <div
                                className="bg-gray-900 rounded-lg p-4 border border-gray-700 hover:border-blue-500 cursor-pointer transition-all"
                                onClick={() => setSelectedNode(selectedNode === index ? null : index)}
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2 mb-1">
                                            <span className="text-xs font-mono text-gray-500">Step {node.step + 1}</span>
                                            {node.status && (
                                                <span className={`text-xs px-2 py-0.5 rounded ${node.status >= 300 && node.status < 400 ? 'bg-yellow-900/50 text-yellow-200' :
                                                    node.status === 200 ? 'bg-green-900/50 text-green-200' : 'bg-gray-800 text-gray-400'
                                                    }`}>
                                                    {node.status}
                                                </span>
                                            )}
                                            {node.cti_data?.verdict && (
                                                <span className={`text-xs px-2 py-0.5 rounded border ${isMalicious
                                                    ? 'bg-red-900/20 border-red-800 text-red-300'
                                                    : isSuspicious
                                                        ? 'bg-orange-900/20 border-orange-800 text-orange-300'
                                                        : 'bg-emerald-900/20 border-emerald-800 text-emerald-300'
                                                    }`}>
                                                    {node.cti_data.verdict}
                                                </span>
                                            )}
                                        </div>
                                        <h3 className="font-mono text-sm text-blue-300 break-all truncate pr-4" title={node.url}>
                                            {node.url}
                                        </h3>
                                    </div>
                                </div>

                                {/* Expanded Details */}
                                {selectedNode === index && (
                                    <div
                                        className="mt-4 pt-4 border-t border-gray-800 space-y-4 animate-in fade-in slide-in-from-top-2"
                                        onClick={(e) => e.stopPropagation()} // Stop click from bubbling to parent (closing the dropdown)
                                    >
                                        {/* Headers */}
                                        <div>
                                            <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">Headers</h4>
                                            <div className="bg-black/30 rounded p-2 overflow-x-auto max-h-40 overflow-y-auto">
                                                <pre className="text-xs text-green-400 font-mono">
                                                    {JSON.stringify(node.headers, null, 2)}
                                                </pre>
                                            </div>
                                        </div>

                                        {/* Body Content */}
                                        {node.body_summary && (
                                            <div>
                                                <div className="flex items-center justify-between mb-2">
                                                    <h4 className="text-xs font-semibold text-gray-400 uppercase flex items-center gap-2">
                                                        <Code className="w-3 h-3" /> Page Content
                                                    </h4>
                                                    <button
                                                        type="button"
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            setExpandedBodyStep(isBodyExpanded ? null : index);
                                                        }}
                                                        className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1"
                                                    >
                                                        {isBodyExpanded ? (
                                                            <>
                                                                Compress <ChevronUp className="w-3 h-3" />
                                                            </>
                                                        ) : (
                                                            <>
                                                                Expand <ChevronDown className="w-3 h-3" />
                                                            </>
                                                        )}
                                                    </button>
                                                </div>
                                                <div className={`bg-black/30 rounded p-2 overflow-x-auto ${isBodyExpanded ? 'max-h-none' : 'max-h-40'} overflow-y-auto transition-all`}>
                                                    <pre className="text-xs text-gray-400 font-mono whitespace-pre-wrap break-words">
                                                        {node.body_summary.substring(0, isBodyExpanded ? 50000 : 5000)}
                                                    </pre>
                                                </div>
                                            </div>
                                        )}

                                        {/* CTI Intelligence */}
                                        {node.cti_data && (
                                            <div>
                                                <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">CTI Intelligence</h4>
                                                <div className="space-y-2">
                                                    {/* VirusTotal */}
                                                    {node.cti_data.sources?.virustotal && (
                                                        <div className="bg-gray-800 p-3 rounded">
                                                            <div className="flex items-center justify-between mb-2">
                                                                <span className="text-sm font-semibold text-blue-300">VirusTotal</span>
                                                                {node.cti_data.sources.virustotal.link && (
                                                                    <a
                                                                        href={node.cti_data.sources.virustotal.link}
                                                                        target="_blank"
                                                                        rel="noopener noreferrer"
                                                                        className="text-xs text-blue-400 hover:underline flex items-center gap-1"
                                                                    >
                                                                        View Report <ExternalLink className="w-3 h-3" />
                                                                    </a>
                                                                )}
                                                            </div>
                                                            <div className="text-xs text-gray-400">
                                                                {node.cti_data.sources.virustotal.error_code === 69 ? (
                                                                    <div className="bg-red-900/40 border border-red-500/50 text-red-200 p-2 rounded flex items-center gap-2 animate-pulse">
                                                                        <span className="text-lg">⚠️</span>
                                                                        <span className="font-semibold">API Error (Code 69): Please check API Key</span>
                                                                    </div>
                                                                ) : node.cti_data.sources.virustotal.stats ? (
                                                                    <div className="grid grid-cols-2 gap-2">
                                                                        <div>Malicious: {node.cti_data.sources.virustotal.stats.malicious || 0}</div>
                                                                        <div>Suspicious: {node.cti_data.sources.virustotal.stats.suspicious || 0}</div>
                                                                        <div>Harmless: {node.cti_data.sources.virustotal.stats.harmless || 0}</div>
                                                                        <div>Undetected: {node.cti_data.sources.virustotal.stats.undetected || 0}</div>
                                                                    </div>
                                                                ) : (
                                                                    <span className="italic">No detailed stats available</span>
                                                                )}
                                                            </div>
                                                        </div>
                                                    )}

                                                    {/* Domain Age (DomainDuck) */}
                                                    {(node.cti_data?.sources?.domainduck) && (
                                                        <div className="bg-gray-800 p-3 rounded border border-gray-700">
                                                            <span className="text-sm font-semibold text-orange-300 block mb-2 flex items-center gap-2">
                                                                <Clock className="w-3 h-3" /> Domain Info
                                                            </span>
                                                            {node.cti_data.sources.domainduck.error_code === 69 ? (
                                                                <div className="bg-red-900/40 border border-red-500/50 text-red-200 p-2 rounded flex items-center gap-2 animate-pulse mt-2">
                                                                    <span className="text-lg">⚠️</span>
                                                                    <span className="font-semibold">API Error (Code 69): Please check API Key</span>
                                                                </div>
                                                            ) : (
                                                                <div className="grid grid-cols-2 gap-2 text-xs text-gray-300">
                                                                    <div>
                                                                        <span className="text-gray-500 block">Creation Date</span>
                                                                        {node.cti_data.sources.domainduck.creation_date
                                                                            ? new Date(node.cti_data.sources.domainduck.creation_date).toLocaleDateString()
                                                                            : 'Unknown'}
                                                                    </div>
                                                                    <div>
                                                                        <span className="text-gray-500 block">Age</span>
                                                                        {node.cti_data.sources.domainduck.age_days >= 0
                                                                            ? `${node.cti_data.sources.domainduck.age_days} days`
                                                                            : 'Unknown'}
                                                                    </div>
                                                                    <div className="col-span-2">
                                                                        <span className="text-gray-500 block">Registrar</span>
                                                                        {node.cti_data.sources.domainduck.registrar || 'Unknown'}
                                                                    </div>
                                                                </div>
                                                            )}
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        )}

                                        {/* Screenshot */}
                                        {node.screenshot && (
                                            <div>
                                                <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2 flex items-center gap-2">
                                                    <Camera className="w-3 h-3" /> Screenshot
                                                </h4>
                                                <div
                                                    className="relative group rounded overflow-hidden border border-gray-700 cursor-zoom-in"
                                                    onClick={(e) => {
                                                        e.stopPropagation(); // Explicitly stop propagation for current element
                                                        setFullscreenImage(node.screenshot);
                                                    }}
                                                >
                                                    <img
                                                        src={`data:image/png;base64,${node.screenshot}`}
                                                        alt="Screenshot"
                                                        className="w-full h-auto object-cover max-h-96"
                                                    />
                                                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                                        <Maximize2 className="w-8 h-8 text-white" />
                                                    </div>
                                                </div>
                                            </div>
                                        )}

                                        {/* Ollama Analysis Summary */}
                                        {summaryReport && index === chain.length - 1 && (
                                            <div>
                                                <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2 flex items-center gap-2">
                                                    <FileText className="w-3 h-3" /> AI Analysis Summary
                                                </h4>
                                                <div className="bg-blue-900/10 border border-blue-800 rounded p-3 text-sm text-gray-300">
                                                    {renderSummary(summaryReport)}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Fullscreen Image Modal */}
            {fullscreenImage && (
                <div
                    className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4 backdrop-blur-sm animate-in fade-in duration-200"
                    onClick={() => setFullscreenImage(null)}
                >
                    <button
                        className="absolute top-4 right-4 text-white/70 hover:text-white transition-colors"
                        onClick={() => setFullscreenImage(null)}
                    >
                        <X className="w-8 h-8" />
                    </button>
                    <img
                        src={`data:image/png;base64,${fullscreenImage}`}
                        alt="Fullscreen Screenshot"
                        className="max-w-full max-h-[90vh] object-contain rounded shadow-2xl"
                    />
                </div>
            )}
        </div>
    );
};

export default RedirectionChain;
