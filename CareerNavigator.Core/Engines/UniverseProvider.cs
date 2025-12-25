using CareerNavigator.Core.Models.Schema;
using Newtonsoft.Json;
using Newtonsoft.Json.Serialization;

namespace CareerNavigator.Core.Engines;

public class UniverseProvider
{
    private readonly Universe _universe;

    public UniverseProvider(IWebHostEnvironment env, ILogger<UniverseProvider> logger)
    {
        var path = Path.Combine(env.ContentRootPath, "Data", "universe.json");
        if (!File.Exists(path))
        {
            _universe = new Universe(); // Return empty to prevent crash
            return;
        }

        try
        {
            var json = File.ReadAllText(path);
            var settings = new JsonSerializerSettings
            {
                // Ensures "seniorityScore" in JSON maps to "SeniorityScore" in C#
                ContractResolver = new CamelCasePropertyNamesContractResolver(),
                NullValueHandling = NullValueHandling.Ignore
            };
            _universe = JsonConvert.DeserializeObject<Universe>(json, settings) 
                        ?? new Universe();

        }
        catch (JsonException ex)
        {
            _universe = new Universe();
        }
        
        catch (Exception ex)
        {
            _universe = new Universe();
        }
    }

    public Universe GetUniverse() => _universe;
}