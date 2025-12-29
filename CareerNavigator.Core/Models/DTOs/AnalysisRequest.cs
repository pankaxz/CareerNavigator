namespace CareerNavigator.Core.Models.DTOs;

public class AnalysisRequest
{
    public string Text { get; set; } = "";

    // Manual Input Support
    public List<string>? ManualSkills { get; set; }
    public int? ManualYearsOfExperience { get; set; }
    public string? AdditionalDetails { get; set; }
}