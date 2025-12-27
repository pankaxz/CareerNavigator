using System.Text.RegularExpressions;
using CareerNavigator.Core.Models.DTOs; // Ensure this namespace exists for the return type
using CareerNavigator.Core.Models.Schema;

namespace CareerNavigator.Core.Engines;

public class SkillScanner
{
    private readonly UniverseProvider _universeProvider;
    private readonly ILogger<SkillScanner> _logger;

    public SkillScanner(UniverseProvider universeProvider, ILogger<SkillScanner> logger)
    {
        _universeProvider = universeProvider;
        _logger = logger;
    }

    /// <summary>
    /// Performs a deep analysis of the user's profile to extract Skills, YOE, and Seniority.
    /// </summary>
    public UserProfile AnalyzeProfile(string text)
    {
        if (string.IsNullOrWhiteSpace(text)) return new UserProfile();

        var profile = new UserProfile
        {
            // 1. Extract Skills (Existing Logic)
            Skills = ScanForSkills(text),

            // 2. Calculate User Seniority (Ported Logic)
            YearsOfExperience = ExtractYearsOfExperience(text)
        };

        // 3. Determine Seniority Status (Rule: 5+ Years = Senior)
        profile.IsSenior = profile.YearsOfExperience >= 5;

        _logger.LogInformation("Profile Analyzed: Found {SkillCount} skills, {Yoe} YOE. Senior: {IsSenior}",
            profile.Skills.Count, profile.YearsOfExperience, profile.IsSenior);

        return profile;
    }

    /// <summary>
    /// Scans the text for known skills from the Universe.
    /// </summary>
    private List<string> ScanForSkills(string text)
    {
        var matchedIds = new List<string>();
        var cleanText = text.ToLower();
        var allSkills = _universeProvider.GetUniverse().Nodes.Select(n => n.Id).ToList();

        foreach (var skillId in allSkills)
        {
            // Use lookarounds (?<!\w) and (?!\w) instead of \b to handle symbols like "C++" or ".NET"
            // \b treats '+' as a non-word char, so "C++ " fails the boundary check.
            string pattern = $@"(?<!\w){Regex.Escape(skillId.ToLower())}(?!\w)";

            if (Regex.IsMatch(cleanText, pattern))
            {
                matchedIds.Add(skillId);
            }
        }
        return matchedIds;
    }

    /// <summary>
    /// Extracts the maximum Years of Experience using the Python DataFactory regex patterns.
    /// </summary>
    private int ExtractYearsOfExperience(string text)
    {
        var cleanText = text.ToLower();
        int maxYears = 0;

        // --- Pattern 1: Senior Experience (5-19 years) ---
        // Matches: "5+ years", "8 yrs", "10 years", "12 years"
        // Python equivalent: r"(5\+|[5-9]|1[0-9])\s*(years|yrs|year)"
        var seniorPattern = @"(5\+|[5-9]|1[0-9])\s*(years|yrs|year)";

        // --- Pattern 2: Mid-Level Experience (3-4 years) ---
        // Matches: "3 years", "4 yrs"
        // Python equivalent: r"(3|4)\s*(years|yrs|year)"
        var midPattern = @"(3|4)\s*(years|yrs|year)";

        // --- Pattern 3: Junior/General (1-2 years) ---
        // Captures general cases like "1 year", "2+ years" to be safe
        var generalPattern = @"([0-9]+)\+?\s*(years|yrs|year)";

        // We combine logic to find the highest number mentioned
        var matches = Regex.Matches(cleanText, generalPattern);

        foreach (Match match in matches)
        {
            // Group 1 contains the number part (e.g., "5" from "5+ years")
            if (int.TryParse(match.Groups[1].Value, out int years))
            {
                if (years > maxYears) maxYears = years;
            }
        }

        return maxYears;
    }
}