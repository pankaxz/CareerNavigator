namespace CareerNavigator.Core.Models.DTOs;

public class JobProfile
{
    public List<string> Skills { get; set; } = new();
    public int YearsOfExperience { get; set; }
    public double ProfileSeniorityScore { get; set; } // 0.0 to 1.0 (Skill-based)
    public string Level { get; set; } = "Junior"; // Junior, Mid, Senior
}
