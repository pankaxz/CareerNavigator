using CareerNavigator.Core.Models.DTOs;

namespace CareerNavigator.Core.Models.DTOs;

public class GapAnalysisRequest
{
    public AnalysisResult UserProfile { get; set; } = new();
    public AnalysisResult JobDescription { get; set; } = new();
}
