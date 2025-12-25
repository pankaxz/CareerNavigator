/**
 * Represents a "Star" (Skill/Technology) in the galaxy.
 */
export interface GalaxyNode {
    id: string;           // e.g., "python"
    group: string;        // e.g., "AI/ML"
    val: number;          // Node size (total JD occurrences)
    seniorityScore: number;
    isSenior: boolean;

    // These are optional properties injected by the Force Graph engine
    x?: number;
    y?: number;
    vx?: number;
    vy?: number;
}

/**
 * Represents the "Gravity" (Relationship) between two skills.
 */
export interface GalaxyLink {
    source: string;       // Matches a Node's ID
    target: string;       // Matches a Node's ID
    value: number;        // Link thickness (co-occurrence count)
    seniorityScore: number;
    isSenior: boolean;
}

/**
 * The full data structure returned by /api/map/universe
 */
export interface Universe {
    nodes: GalaxyNode[];
    links: GalaxyLink[];
}

/**
 * The response from /api/navigator/analyze
 */
export interface AnalysisResponse {
    matchedSkills: string[]; // List of IDs like ["python", "docker"]
}