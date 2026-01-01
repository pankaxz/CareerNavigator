namespace CareerNavigator.Core.Models.DTOs;

public class AnalysisResult
{
    public List<string> Skills { get; set; } = [];
    public int YearsOfExperience { get; set; }
    public double ProfileSeniorityScore { get; set; } // 0.0 to 1.0 (Skill-based)
    public string Level { get; set; } = "Junior"; // Junior, Mid, Senior

    // Metadata for API Response
    public string Type { get; set; } = "";
    public List<string>? BridgeSkills { get; set; }
}
