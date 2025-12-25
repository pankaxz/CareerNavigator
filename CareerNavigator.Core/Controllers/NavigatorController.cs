using CareerNavigator.Core.Engines;
using CareerNavigator.Core.Models.DTOs;
using Microsoft.AspNetCore.Mvc;

namespace CareerNavigator.Core.Controllers;

[ApiController]
[Route("api/[controller]")] // This maps to "api/navigator"
public class NavigatorController : ControllerBase
{
    private readonly SkillScanner _scanner;

    public NavigatorController(SkillScanner scanner)
    {
        _scanner = scanner;
    }

    // Matches "api/navigator/analyze" AND "api/navigator/analyze/"
    [HttpPost("analyze")]
    public IActionResult Analyze([FromBody] AnalysisRequest request)
    {
        if (request == null || string.IsNullOrWhiteSpace(request.Text))
        {
            return BadRequest("Resume text is required.");
        }

        var foundSkills = _scanner.FindMatches(request.Text);
        
        // Return the list of matched Node IDs
        return Ok(foundSkills);
    }
}