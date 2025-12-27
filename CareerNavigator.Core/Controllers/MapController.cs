using CareerNavigator.Core.Engines;
using Microsoft.AspNetCore.Mvc;

namespace CareerNavigator.Core.Controllers;

[ApiController]
[Route("api/[controller]")] // This makes the URL "api/map"
public class MapController : ControllerBase
{
    private readonly IUniverseProvider _universeProvider;

    public MapController(IUniverseProvider universeProvider)
    {
        _universeProvider = universeProvider;
    }

    [HttpGet("universe")] // This makes the URL "api/map/universe"
    public IActionResult GetUniverse()
    {
        var universe = _universeProvider.GetUniverse();
        return Ok(universe);
    }
}