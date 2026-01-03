using CareerNavigator.Core.Engines;
using CareerNavigator.Core.Models.DTOs;
using Microsoft.AspNetCore.Mvc;

namespace CareerNavigator.Core.Controllers;

/// <summary>
/// The primary API Controller for CareerNavigator. Exposes endpoints for analysis and gap detection.
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class NavigatorController : ControllerBase
{
    private readonly SkillScanner _scanner;
    private readonly BridgeEngine _bridgeEngine;
    private readonly GapAnalyzer _gapAnalyzer;

    /// <summary>
    /// Initializes a new instance of the <see cref="NavigatorController"/> class.
    /// </summary>
    /// <param name="scanner">Engine for text analysis.</param>
    /// <param name="bridgeEngine">Engine for finding skill bridges.</param>
    /// <param name="gapAnalyzer">Engine for comparing profiles.</param>
    public NavigatorController(SkillScanner scanner, BridgeEngine bridgeEngine, GapAnalyzer gapAnalyzer)
    {
        _scanner = scanner;
        _bridgeEngine = bridgeEngine;
        _gapAnalyzer = gapAnalyzer;
    }

    /// <summary>
    /// Analyzes a user profile text (resume/bio) to extract skills and seniority.
    /// </summary>
    /// <param name="request">The input text and optional manual overrides.</param>
    /// <returns>A detailed analysis including detected skills, seniority level, and suggested bridge skills.</returns>
    [HttpPost("analyze/profile")]
    public IActionResult AnalyzeProfile([FromBody] AnalysisRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.Text)) return BadRequest("Text required");

        // 1. Analyze User Profile
        AnalysisResult profile = _scanner.AnalyzeProfile(request);

        // 2. Suggest Bridges (Only relevant for users)
        profile.BridgeSkills = _bridgeEngine.SuggestBridges(profile);
        profile.Type = "User Profile";

        return Ok(profile);
    }

    /// <summary>
    /// Analyzes a job description to extract required skills and seniority.
    /// </summary>
    /// <param name="request">The job description text.</param>
    /// <returns>A detailed analysis of the job requirements.</returns>
    [HttpPost("analyze/job")]
    public IActionResult AnalyzeJob([FromBody] AnalysisRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.Text)) return BadRequest("Text required");

        // 1. Analyze Job Description
        // Note: Manual overrides like YOE are less relevant for JD parsing but supported by the request object if needed.
        // We assume the text itself is the job description.
        AnalysisResult result = _scanner.AnalyzeJob(request);

        result.Type = "Job Description";

        return Ok(result);
    }

    /// <summary>
    /// Calculates the skill and seniority gap between a user profile and a job description.
    /// </summary>
    /// <param name="request">Contains both the User Profile and Job Description analysis results.</param>
    /// <returns>A report detailing missing skills, implicit dependencies, and seniority alignment.</returns>
    [HttpPost("analyze/gap")]
    public IActionResult AnalyzeGap([FromBody] GapAnalysisRequest request)
    {
        var result = _gapAnalyzer.AnalyzeGap(request.UserProfile, request.JobDescription);
        return Ok(result);
    }
}