using System.Text.RegularExpressions;
using Microsoft.Extensions.Logging;
using CareerNavigator.Core.Models.DTOs; // Ensure you have a UserProfile DTO

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

    public UserProfile AnalyzeProfile(string text)
    {
        var profile = new UserProfile();

        // 1. Extract Skills (Existing Logic)
        profile.Skills = ScanForSkills(text);

        // 2. Calculate User Seniority (Ported Logic)
        profile.YearsOfExperience = ExtractYearsOfExperience(text);
        profile.IsSenior = profile.YearsOfExperience >= 5;

        return profile;
    }

    private int ExtractYearsOfExperience(string text)
    {
        // Regex ported from your Python TextProcessor
        // Matches: "5+ years", "5 years", "10 yrs"
        var expPattern = @"(1[0-9]|[1-9])\+?\s*(years|yrs|year)";

        var matches = Regex.Matches(text.ToLower(), expPattern);
        int maxYears = 0;

        foreach (Match match in matches)
        {
            // Parse the number part (e.g., "5" from "5+ years")
            if (int.TryParse(match.Groups[1].Value, out int years))
            {
                if (years > maxYears) maxYears = years;
            }
        }
        return maxYears;
    }

    private List<string> ScanForSkills(string text)
    {
        // ... (Your existing scanning logic) ...
        return new List<string>(); // Placeholder
    }
}

// Simple DTO to return to Frontend
public class UserProfile
{
    public List<string> Skills { get; set; } = new();
    public int YearsOfExperience { get; set; }
    public bool IsSenior { get; set; }
}