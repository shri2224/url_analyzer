import React from 'react';
import { FlaskConical, Beaker } from 'lucide-react';

const TestLab = () => {
    return (
        <div className="p-8 max-w-6xl mx-auto">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                    <FlaskConical className="text-purple-400" /> Test Lab
                </h1>
                <p className="text-gray-500 mt-1 text-sm">
                    Sandbox for prototyping new features
                </p>
            </div>

            {/* Empty State */}
            <div className="text-center py-24 border border-dashed border-gray-700 rounded-xl bg-gray-900/30">
                <Beaker className="mx-auto text-gray-700 mb-4" size={56} />
                <p className="text-gray-400 text-lg font-semibold">Nothing here yet</p>
                <p className="text-gray-600 text-sm mt-2 max-w-md mx-auto">
                    This space is reserved for testing new features before they go live.
                    Drop your next experiment here.
                </p>
            </div>
        </div>
    );
};

export default TestLab;
