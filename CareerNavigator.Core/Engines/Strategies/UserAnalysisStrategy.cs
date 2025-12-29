using System.Text.RegularExpressions;
using CareerNavigator.Core.Models.DTOs;
using CareerNavigator.Core.Models.Schema;

namespace CareerNavigator.Core.Engines.Strategies;

public class UserAnalysisStrategy : BaseAnalysisStrategy
{
    protected override double CalculateSeniorityScore(List<string> skillIds, string text, IUniverseProvider universeProvider)
    {
        var matchedNodes = universeProvider.GetUniverse().Nodes
            .Where(n => skillIds.Contains(n.Id))
            .ToList();

        if (!matchedNodes.Any()) return 0.0;

        var baseScore = matchedNodes.Average(n => n.SeniorityScore);

        // BOOST: Check for leadership action verbs
        // "Architected", "Designed", "Led", "Managed", "Founded"
        double leadBoost = 0;
        if (Regex.IsMatch(text, @"\b(architected|designed|led|managed|headed|founded|orchestrated)\b", RegexOptions.IgnoreCase))
        {
            leadBoost = 0.15; // Significant boost
        }
        else if (Regex.IsMatch(text, @"\b(senior|principal|staff|lead)\b", RegexOptions.IgnoreCase))
        {
            leadBoost = 0.1; // Keyword boost
        }

        return Math.Min(1.0, baseScore + leadBoost);
    }

    protected override string DetermineLevel(int years, double score, string text)
    {
        // Explicit Override: Trust self-identified titles in likely context
        // This aligns behavior with JobDescriptionAnalysisStrategy
        if (text.Contains("senior") || text.Contains("principal") || text.Contains("staff") || text.Contains("architect"))
        {
            return "Senior";
        }

        if (text.Contains("lead"))
        {
            // "Lead" can be ambiguous ("Lead developer" vs "I lead a team"), but mostly implies Senior level responsibility
            return "Senior";
        }

        return base.DetermineLevel(years, score, text);
    }
}
