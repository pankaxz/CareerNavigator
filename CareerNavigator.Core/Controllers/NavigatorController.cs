using CareerNavigator.Core.Engines;
using CareerNavigator.Core.Models.DTOs;
using Microsoft.AspNetCore.Mvc;

namespace CareerNavigator.Core.Controllers;

[ApiController]
[Route("api/[controller]")]
public class NavigatorController : ControllerBase
{
    private readonly SkillScanner _scanner;
    private readonly UniverseProvider _universeProvider;

    public NavigatorController(SkillScanner scanner, UniverseProvider universeProvider)
    {
        _scanner = scanner;
        _universeProvider = universeProvider;
    }

    [HttpPost("analyze")]
    public IActionResult Analyze([FromBody] AnalysisRequest request)
    {
        if (request == null || string.IsNullOrWhiteSpace(request.Text))
        {
            return BadRequest("Resume text is required.");
        }
        var userProfile = _scanner.AnalyzeProfile(request.Text);

        // Get the graph logic
        var universe = _universeProvider.GetUniverse();

        // Find "Gap" Skills:
        // Skills connected to user's current skills BUT require higher seniority
        var bridgeSkills = new List<string>();

        foreach (var skillId in userProfile.Skills)
        {
            // Find neighbors in the graph
            var neighbors = universe.Links
                .Where(l => l.Source == skillId || l.Target == skillId)
                .Select(l => l.Source == skillId ? l.Target : l.Source);

            foreach (var neighborId in neighbors)
            {
                var neighborNode = universe.Nodes.FirstOrDefault(n => n.Id == neighborId);

                // LOGIC: If neighbor is Senior, but User is Junior -> It's a BRIDGE Skill
                if (neighborNode != null && neighborNode.IsSenior && !userProfile.IsSenior)
                {
                    bridgeSkills.Add(neighborId);
                }
            }
        }

        return Ok(new
        {
            userProfile.Skills,
            userProfile.YearsOfExperience,
            BridgeSkills = bridgeSkills.Distinct().Take(3) // Suggest top 3
        });
    }
}
