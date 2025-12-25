using System.Text.RegularExpressions;
using CareerNavigator.Core.Models.Schema;

namespace CareerNavigator.Core.Engines;

public class SkillScanner
{
    private readonly UniverseProvider _universeProvider;

    public SkillScanner(UniverseProvider universeProvider)
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
            // \b ensures we match the whole word only.
            // Regex.Escape handles special chars like C++ or .NET
            string pattern = $@"\b{Regex.Escape(skillId.ToLower())}\b";
            
            if (Regex.IsMatch(cleanText, pattern))
            {
                matchedIds.Add(skillId);
            }
        }

        return matchedIds;
    }
}