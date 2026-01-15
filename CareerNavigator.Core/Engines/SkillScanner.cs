using CareerNavigator.Core.Models.DTOs;
using CareerNavigator.Core.Models.Schema;
using CareerNavigator.Core.Engines.Strategies;

namespace CareerNavigator.Core.Engines;

/// <summary>
/// Orchestrates the process of analyzing text to extract skill and seniority metadata.
/// </summary>
/// <remarks>
/// Acts as the high-level façade for the analysis subsystem. It coordinates:
/// <list type="bullet">
/// <item><description><see cref="SkillParser"/> for raw entity extraction.</description></item>
/// <item><description><see cref="IAnalysisStrategy"/> for context-specific logic (User vs. Job).</description></item>
/// <item><description><see cref="IUniverseProvider"/> for graph-based enrichment.</description></item>
/// </list>
/// </remarks>
public class SkillScanner
{
    private readonly SkillParser _parser;
    private readonly IUniverseProvider _universeProvider;
    private readonly IAnalysisStrategy _userStrategy = new UserAnalysisStrategy();
    private readonly IAnalysisStrategy _jobStrategy = new JobDescriptionAnalysisStrategy();

    /// <summary>
    /// Initializes a new instance of the <see cref="SkillScanner"/> class.
    /// </summary>
    /// <param name="parser">The regex-based parser for identifying skills in text.</param>
    /// <param name="universeProvider">The provider for accessing the skill graph universe.</param>
    public SkillScanner(SkillParser parser, IUniverseProvider universeProvider)
    {
        _parser = parser;
        _universeProvider = universeProvider;
    }

    /// <summary>
    /// Analyzes a user's resume or profile text.
    /// </summary>
    /// <param name="text">The raw text of the resume/profile.</param>
    /// <returns>A structured <see cref="AnalysisResult"/> containing identified skills and seniority.</returns>
    public AnalysisResult AnalyzeProfile(string text)
    {
        return AnalyzeProfile(new AnalysisRequest { Text = text });
    }

    /// <summary>
    /// Analyzes a user profile request, potentially including manual overrides.
    /// </summary>
    /// <param name="request">The analysis request object.</param>
    /// <returns>A structured <see cref="AnalysisResult"/> representing the user's profile.</returns>
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


    /// <summary>
    /// Analyzes a job description text.
    /// </summary>
    /// <param name="text">The raw job description text.</param>
    /// <returns>A structured <see cref="AnalysisResult"/> representing the job's requirements.</returns>
    public AnalysisResult AnalyzeJob(string text)
    {
        return AnalyzeJob(new AnalysisRequest { Text = text });
    }

    /// <summary>
    /// Analyzes a job description request, potentially including manual overrides.
    /// </summary>
    /// <param name="request">The analysis request object.</param>
    /// <returns>A structured <see cref="AnalysisResult"/> representing the job's requirements.</returns>
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