using System.Text.RegularExpressions;
using CareerNavigator.Core.Models.DTOs;
using CareerNavigator.Core.Models.Schema;

namespace CareerNavigator.Core.Engines.Strategies;

public abstract class BaseAnalysisStrategy : IAnalysisStrategy
{
    public virtual AnalysisResult Analyze(AnalysisRequest request, List<string> skillIds, IUniverseProvider universeProvider)
    {
        var text = request.Text ?? "";

        // Manual YOE Override: Use it if present, otherwise extract
        var yearsOfExperience = request.ManualYearsOfExperience ?? ExtractYearsOfExperience(text);

        // Pass text (or combined details) to calculation logic
        // We use request.Text + AdditionalDetails as context for strategies
        var contextText = (text + "\n" + (request.AdditionalDetails ?? "")).ToLower();

        var seniorityScore = CalculateSeniorityScore(skillIds, contextText, universeProvider);

        return new AnalysisResult
        {
            Skills = skillIds,
            YearsOfExperience = yearsOfExperience,
            ProfileSeniorityScore = seniorityScore,
            Level = DetermineLevel(yearsOfExperience, seniorityScore, contextText)
        };
    }

    protected virtual int ExtractYearsOfExperience(string text)
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

    protected virtual double CalculateSeniorityScore(List<string> skillIds, string text, IUniverseProvider universeProvider)
    {
        var universe = universeProvider.GetUniverse();
        var matchedNodes = new List<Node>();

        foreach (var skillId in skillIds)
        {
            if (universe.NodeIndex.TryGetValue(skillId, out var node))
            {
                matchedNodes.Add(node);
            }
        }

        if (!matchedNodes.Any()) return 0.0;

        return matchedNodes.Average(n => n.SeniorityScore);
    }

    protected virtual string DetermineLevel(int years, double score, string text)
    {
        // Default heuristics
        if (years >= 5 || score > 0.7) return "Senior";
        if (years >= 3 || score > 0.4) return "Mid";
        return "Junior";
    }
}
