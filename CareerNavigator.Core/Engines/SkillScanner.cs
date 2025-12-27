using System.Text.RegularExpressions;
using CareerNavigator.Core.Models.DTOs;
using CareerNavigator.Core.Models.Schema;

namespace CareerNavigator.Core.Engines;

public class SkillScanner
{
    private readonly IUniverseProvider _universeProvider;
    private Dictionary<string, Regex> _regexCache = new Dictionary<string, Regex>();
    private Universe? _lastUniverse;

    public SkillScanner(IUniverseProvider universeProvider)
    {
        _universeProvider = universeProvider;
    }

    public JobProfile AnalyzeProfile(string text)
    {
        if (string.IsNullOrWhiteSpace(text)) return new JobProfile();

        var cleanText = text.ToLower();
        // 1. Extract raw data
        var skills = ScanForSkills(cleanText);

        // 2. Extract Years of Experience
        var yearsOfExperience = ExtractYearsOfExperience(cleanText);

        // 3. Calculate Seniority Score
        var seniorityScore = CalculateSeniorityScore(skills);

        // 4. Construct and return profile
        return new JobProfile
        {
            Skills = skills,
            YearsOfExperience = yearsOfExperience,
            ProfileSeniorityScore = seniorityScore,
            Level = DetermineLevel(yearsOfExperience, seniorityScore)
        };
    }

    private double CalculateSeniorityScore(List<string> skillIds)
    {
        var matchedNodes = _universeProvider.GetUniverse().Nodes
            .Where(n => skillIds.Contains(n.Id))
            .ToList();


        if (matchedNodes.Any())
        {
            return matchedNodes.Average(n => n.SeniorityScore);
        }
        return 0.0;
    }

    private string DetermineLevel(int years, double score)
    {
        if (years >= 5 || score > 0.7)
        {
            return "Senior";
        }

        if (years >= 3 || score > 0.4)
        {
            return "Mid";
        }

        return "Junior";
    }

    private List<string> ScanForSkills(string text)
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
            if (!_regexCache.TryGetValue(node.Id, out var patternRegex))
            {
                var pattern = GenerateSkillRegex(node.Id);
                patternRegex = new Regex(pattern, RegexOptions.IgnoreCase);
                _regexCache[node.Id] = patternRegex;
                Console.WriteLine($"Generated regex for {node.Id}: {pattern}");
            }

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

    //TODO : add consideration for more than one YOE, like management YOE of 4 years and Work YOE of 10 years.
    private int ExtractYearsOfExperience(string text)
    {
        int maxYears = 0;

        // Combined pattern to catch "5+ years", "10 yrs", "3 years"
        var pattern = @"(\d+)\+?\s*(years|yrs|year)";

        var matches = Regex.Matches(text, pattern);
        foreach (Match match in matches)
        {
            if (int.TryParse(match.Groups[1].Value, out int years))
            {
                // Sanity check: Ignore "2023 years" or unrealistic numbers
                if (years < 40 && years > maxYears)
                {
                    maxYears = years;
                }
            }
        }
        return maxYears;
    }
}