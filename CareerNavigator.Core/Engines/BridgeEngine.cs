using CareerNavigator.Core.Models.DTOs;

namespace CareerNavigator.Core.Engines;

public class BridgeEngine
{
    private readonly IUniverseProvider _universeProvider;

    public BridgeEngine(IUniverseProvider universeProvider)
    {
        _universeProvider = universeProvider;
    }

    public List<string> SuggestBridges(AnalysisResult profile)
    {
        var universe = _universeProvider.GetUniverse();
        var candidateSkills = new Dictionary<string, double>();
        var mySkillsSet = new HashSet<string>(profile.Skills, StringComparer.OrdinalIgnoreCase);

        //Traverse through the skills detected from the profile.
        foreach (var mySkill in profile.Skills)
        {
            if (!universe.AdjacencyList.TryGetValue(mySkill, out var links)) continue;

            foreach (var link in links)
            {
                var neighborId = link.Source.Equals(mySkill, StringComparison.OrdinalIgnoreCase) ? link.Target : link.Source;

                if (mySkillsSet.Contains(neighborId)) continue;

                // O(1) Lookup for Node properties
                if (!universe.NodeIndex.TryGetValue(neighborId, out var neighborNode)) continue;

                double relevance = link.Value;

                // Boost for seniority gap
                if (neighborNode.IsSenior && profile.Level != "Senior")
                {
                    relevance *= 1.5;
                }

                if (!candidateSkills.ContainsKey(neighborId))
                    candidateSkills[neighborId] = 0;

                candidateSkills[neighborId] += relevance;
            }
        }

        return candidateSkills
            .OrderByDescending(x => x.Value)
            .Take(3)
            .Select(x => x.Key)
            .ToList();
    }
}
