"use client";
import dynamic from 'next/dynamic';
import { useGalaxyStore } from '@/store/useGalaxyStore';
import { useNavigation } from '@/hooks/useNavigation';
import { useEffect, useRef } from 'react';
import { ForceGraphMethods } from 'react-force-graph-2d';

// Load ForceGraph only on the client
const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), { ssr: false });

export default function Universe() {
    const { universe, userSkills, isSeniorView } = useGalaxyStore();
    const { fetchUniverse } = useNavigation();
    const graphRef = useRef<ForceGraphMethods | null>(null);

    useEffect(() => {
        graphRef.current?.zoomToFit(400);
    }, [universe]);

    useEffect(() => {
        fetchUniverse();
    }, []);

    if (!universe) return <div className="text-white p-10">Initializing Galaxy...</div>;

    return (
        <div className="w-full h-screen bg-[#050505]">
            <ForceGraph2D
                ref={graphRef}
                graphData={universe}
                backgroundColor="#050505"
                nodeLabel="id"

                // --- Visual Logic ---
                nodeRelSize={6}
                nodeColor={(node: any) => {
                    // Highlight user skills in Green
                    if (userSkills && userSkills.includes(node.id)) return "#00FF00";
                    // Dim senior nodes if toggle is off
                    if (node.isSenior && !isSeniorView) return "#1A1A1A";
                    return "#444444";
                }}

                // --- The "Obsidian" Glow ---
                nodeCanvasObject={(node: any, ctx, globalScale) => {
                    const label = node.id;
                    const fontSize = 12 / globalScale;
                    ctx.font = `${fontSize}px Inter, sans-serif`;

                    // Only show labels for owned skills or when zoomed in
                    const shouldShowLabel = (userSkills && userSkills.includes(node.id)) || globalScale > 1.5;

                    // Draw Glow for Green nodes
                    if (userSkills && userSkills.includes(node.id)) {
                        ctx.shadowColor = "#00FF00";
                        ctx.shadowBlur = 15;
                    } else {
                        ctx.shadowBlur = 0;
                    }

                    ctx.beginPath();
                    ctx.arc(node.x, node.y, 3, 0, 2 * Math.PI, false);
                    ctx.fillStyle = (userSkills && userSkills.includes(node.id)) ? "#00FF00" : "#444444";
                    ctx.fill();

                    if (shouldShowLabel) {
                        ctx.fillStyle = "rgba(255, 255, 255, 0.8)";
                        ctx.fillText(label, node.x + 6, node.y + 3);
                    }
                }}

                // --- Link Logic ---
                linkColor={() => "rgba(255, 255, 255, 0.05)"}
                linkWidth={1}
            />
        </div>
    );
}