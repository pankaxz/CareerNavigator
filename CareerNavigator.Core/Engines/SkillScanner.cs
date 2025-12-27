using System.Text.RegularExpressions;
using CareerNavigator.Core.Models.Schema;

namespace CareerNavigator.Core.Engines;

public class SkillScanner
{
    private readonly IUniverseProvider _universeProvider;

    public SkillScanner(IUniverseProvider universeProvider)
    {
        _universeProvider = universeProvider;
    }

    public List<string> FindMatches(string text)
    {
        var matchedIds = new List<string>();

        if (string.IsNullOrWhiteSpace(text)) return matchedIds;

        // 1. Get all valid skill IDs from our loaded map
        var allSkills = _universeProvider.GetUniverse().Nodes.Select(n => n.Id).ToList();

        // 2. Prepare text for matching
        var cleanText = text.ToLower();

        // 3. Scan for each skill
        foreach (var skillId in allSkills)
        {
            // Use lookarounds (?<!\w) and (?!\w) instead of \b to handle symbols like "C++" or ".NET"
            string pattern = $@"(?<!\w){Regex.Escape(skillId.ToLower())}(?!\w)";

            if (Regex.IsMatch(cleanText, pattern))
            {
                matchedIds.Add(skillId);
            }
        }

        return matchedIds;
    }
}