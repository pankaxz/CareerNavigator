import { create } from 'zustand';
import { Universe } from '@/types';

interface GalaxyState {
    universe: Universe | null;
    userSkills: string[]; // IDs of skills found in the resume
    isSeniorView: boolean;

    // Actions
    setUniverse: (data: Universe) => void;
    setUserSkills: (skills: string[]) => void;
    setSeniorView: (val: boolean) => void;
}

export const useGalaxyStore = create<GalaxyState>((set) => ({
    universe: null,
    userSkills: [],
    isSeniorView: false,

    setUniverse: (data) => set({ universe: data }),
    setUserSkills: (skills) => set({ userSkills: skills }),
    setSeniorView: (val) => set({ isSeniorView: val }),
}));
