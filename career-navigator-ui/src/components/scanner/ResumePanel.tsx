"use client";
import { useState } from 'react';
import { useNavigation } from '@/hooks/useNavigation';

export default function ResumePanel() {
    const [text, setText] = useState("");
    const { analyzeResume } = useNavigation();

    return (
        <div className="p-4 bg-black/60 backdrop-blur-xl border border-white/10 rounded-2xl w-80 shadow-2xl">
            <h3 className="text-white text-sm font-medium mb-3">Analyze Skill DNA</h3>
            <textarea
                className="w-full h-32 bg-black/40 border border-white/5 rounded-lg p-3 text-xs text-white placeholder:text-gray-600 focus:outline-none focus:border-green-500/50 transition-colors"
                placeholder="Paste your resume or JD text here..."
                value={text}
                onChange={(e) => setText(e.target.value)}
            />
            <button
                onClick={() => analyzeResume(text)}
                className="w-full mt-3 py-2 bg-white text-black text-xs font-bold rounded-lg hover:bg-green-500 transition-colors"
            >
                SCAN GALAXY
            </button>
        </div>
    );
}