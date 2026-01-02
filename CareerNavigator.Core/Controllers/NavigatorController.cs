using CareerNavigator.Core.Engines;
using CareerNavigator.Core.Models.DTOs;
using Microsoft.AspNetCore.Mvc;

namespace CareerNavigator.Core.Controllers;

[ApiController]
[Route("api/[controller]")]
public class NavigatorController : ControllerBase
{
    private readonly SkillScanner _scanner;
    private readonly BridgeEngine _bridgeEngine;
    private readonly GapAnalyzer _gapAnalyzer;

    public NavigatorController(SkillScanner scanner, BridgeEngine bridgeEngine, GapAnalyzer gapAnalyzer)
    {
        _scanner = scanner;
        _bridgeEngine = bridgeEngine;
        _gapAnalyzer = gapAnalyzer;
    }

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

    [HttpPost("analyze/gap")]
    public IActionResult AnalyzeGap([FromBody] GapAnalysisRequest request)
    {
        var result = _gapAnalyzer.AnalyzeGap(request.UserProfile, request.JobDescription);
        return Ok(result);
    }
}