using System.Collections.Concurrent;
using System.Text.RegularExpressions;
using CareerNavigator.Core.Models.Schema;

namespace CareerNavigator.Core.Engines;

public class SkillParser
{
    private readonly IUniverseProvider _universeProvider;
    private ConcurrentDictionary<string, Regex> _regexCache = new ConcurrentDictionary<string, Regex>();
    private Universe? _lastUniverse;

    public SkillParser(IUniverseProvider universeProvider)
    {
        _universeProvider = universeProvider;
    }

    public List<string> ParseSkills(string text)
    {
        var matchedIds = new List<string>();
        var currentUniverse = _universeProvider.GetUniverse();

        // 1. Invalidation: If the universe changed, wipe the slate clean
        if (currentUniverse != _lastUniverse)
        {
            _regexCache.Clear();
            _lastUniverse = currentUniverse;
        }

        // Optimisation: Cache loop
        foreach (var node in currentUniverse.Nodes)
        {
            var patternRegex = _regexCache.GetOrAdd(node.Id, id =>
            {
                var pattern = GenerateSkillRegex(id);
                return new Regex(pattern, RegexOptions.IgnoreCase);
            });

            if (patternRegex.IsMatch(text))
            {
                matchedIds.Add(node.Id);
            }
        }
        return matchedIds;
    }

    private string GenerateSkillRegex(string skillId)
    {
        var escaped = Regex.Escape(skillId);

        // Start Boundary
        // Use standard regex lookbehind for word boundary
        var startBoundary = @"(?<!\w)";

        // End Boundary
        // Critical for "C" vs "C++" vs "C#"
        // If skill ends in a word char (e.g. "C"), we must ensure next char is NOT a word char AND not a special skill char (#, +).
        string endBoundary;

        char lastChar = skillId.Last();
        if (char.IsLetterOrDigit(lastChar) || lastChar == '_')
        {
            // Ends in word char: Ensure next is NOT \w AND NOT [#+]
            endBoundary = @"(?![a-zA-Z0-9_+#])";
        }
        else
        {
            // Ends in symbol: Just standard boundary ensures we don't merge into a word
            endBoundary = @"(?!\w)";
        }

        return $"{startBoundary}{escaped}{endBoundary}";
    }
}
