using CareerNavigator.Core.Models.DTOs;
using CareerNavigator.Core.Models.Schema;
using CareerNavigator.Core.Engines.Strategies;

namespace CareerNavigator.Core.Engines;

public class SkillScanner
{
    private readonly SkillParser _parser;
    private readonly IUniverseProvider _universeProvider;

    private readonly IAnalysisStrategy _userStrategy = new UserAnalysisStrategy();
    private readonly IAnalysisStrategy _jobStrategy = new JobDescriptionAnalysisStrategy();

    public SkillScanner(SkillParser parser, IUniverseProvider universeProvider)
    {
        _parser = parser;
        _universeProvider = universeProvider;
    }

    public AnalysisResult AnalyzeProfile(string text)
    {
        return AnalyzeProfile(new AnalysisRequest { Text = text });
    }

    public AnalysisResult AnalyzeProfile(AnalysisRequest request)
    {
        var text = request.Text ?? "";
        var cleanText = text.ToLower();

        // 1. Extract raw data (Manual overrides extraction)
        var skills = request.ManualSkills != null && request.ManualSkills.Any()
            ? request.ManualSkills
            : _parser.ParseSkills(cleanText);

        // 2. Delegate to Strategy
        return _userStrategy.Analyze(request, skills, _universeProvider);
    }

    public AnalysisResult AnalyzeJob(string text)
    {
        return AnalyzeJob(new AnalysisRequest { Text = text });
    }

    public AnalysisResult AnalyzeJob(AnalysisRequest request)
    {
        var text = request.Text ?? "";
        if (string.IsNullOrWhiteSpace(text)) return new AnalysisResult();

        var cleanText = text.ToLower();

        // 1. Extract raw data (Manual overrides extraction)
        var skills = request.ManualSkills != null && request.ManualSkills.Any()
            ? request.ManualSkills
            : _parser.ParseSkills(cleanText);

        return _jobStrategy.Analyze(request, skills, _universeProvider);
    }
}