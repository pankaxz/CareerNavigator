namespace CareerNavigator.Core.Models.DTOs;

public class GapAnalysisResult
{
    public List<string> MissingSkills { get; set; } = new();
    public List<string> ImplicitSkills { get; set; } = new();
    public bool SeniorityMismatch { get; set; }
    public string Message { get; set; } = "";
}
