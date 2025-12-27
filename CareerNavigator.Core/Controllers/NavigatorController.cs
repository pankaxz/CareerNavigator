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

    [HttpPost("analyze")]
    public IActionResult Analyze([FromBody] AnalysisRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.Text)) return BadRequest("Text required");

        // 1. Understand the User
        JobProfile profile = _scanner.AnalyzeProfile(request.Text);

        // 2. Find the Bridges
        var bridgeSkills = _bridgeEngine.SuggestBridges(profile);

        return Ok(new
        {
            skills = profile.Skills,
            yearsOfExperience = profile.YearsOfExperience,
            level = profile.Level,
            bridgeSkills
        });
    }
}