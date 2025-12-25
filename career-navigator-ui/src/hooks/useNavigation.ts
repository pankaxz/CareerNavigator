import { useGalaxyStore } from '@/store/useGalaxyStore';

export const useNavigation = () => {
    const { setUniverse, setUserSkills } = useGalaxyStore();

    const fetchUniverse = async () => {
        try {
            // Point this to your C# API port (e.g., 5128)
            const res = await fetch('http://localhost:5128/api/map/universe');
            const data = await res.json();
            setUniverse(data);
        } catch (err) {
            console.error("Failed to load the galaxy map:", err);
        }
    };

    const analyzeResume = async (text: string) => {
        console.log("Clicked analyze", text);
        try {
            const res = await fetch('http://localhost:5128/api/navigator/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text }),
            });
            const data = await res.json();
            console.log("Analysis result:", data);
            setUserSkills(data.matchedSkills || []);
        } catch (err) {
            console.error("Analysis failed:", err);
        }
    };

    return { fetchUniverse, analyzeResume };
};