import Universe from '@/components/galaxy/Universe';
import ResumePanel from "@/components/scanner/ResumePanel";

export default function Home() {
  return (
      <main className="relative w-full h-screen overflow-hidden">
        {/* The Map Layer */}
        <Universe />

        {/* The UI Overlay Layer */}
        <div className="absolute top-8 left-8 z-10 pointer-events-none">
          <h1 className="text-2xl font-bold text-white tracking-tighter">
            CAREER<span className="text-green-500">NAVIGATOR</span>
          </h1>
          <p className="text-sm text-gray-500 uppercase tracking-widest">Market Intelligence V0.01</p>
        </div>

        {/* Floating Action Panel */}
        <div className="absolute bottom-8 right-8 z-20">
          <ResumePanel />
        </div>
      </main>
  );
}