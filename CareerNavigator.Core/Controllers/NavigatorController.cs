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

    public NavigatorController(SkillScanner scanner, BridgeEngine bridgeEngine)
    {
        _scanner = scanner;
        _bridgeEngine = bridgeEngine;
    }

    [HttpPost("analyze/profile")]
    public IActionResult AnalyzeProfile([FromBody] AnalysisRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.Text)) return BadRequest("Text required");

        // 1. Analyze User Profile
        AnalysisResult profile = _scanner.AnalyzeProfile(request);

        // 2. Suggest Bridges (Only relevant for users)
        var bridgeSkills = _bridgeEngine.SuggestBridges(profile);

        return Ok(new
        {
            type = "User Profile",
            skills = profile.Skills,
            yearsOfExperience = profile.YearsOfExperience,
            level = profile.Level,
            bridgeSkills
        });
    }

    [HttpPost("analyze/job")]
    public IActionResult AnalyzeJob([FromBody] AnalysisRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.Text)) return BadRequest("Text required");

        // 1. Analyze Job Description
        // Note: Manual overrides like YOE are less relevant for JD parsing but supported by the request object if needed.
        // We assume the text itself is the job description.
        AnalysisResult result = _scanner.AnalyzeJob(request);

        return Ok(new
        {
            type = "Job Description",
            skills = result.Skills,
            level = result.Level,
            // Gap analysis isn't relevant for a JD on its own, so no bridge skills.
        });
    }
}