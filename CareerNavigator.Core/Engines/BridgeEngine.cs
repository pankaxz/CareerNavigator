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

        foreach (var mySkill in profile.Skills)
        {
            var links = universe.Links.Where(l => l.Source == mySkill || l.Target == mySkill);

            foreach (var link in links)
            {
                var neighborId = link.Source == mySkill ? link.Target : link.Source;

                if (profile.Skills.Contains(neighborId)) continue;

                var neighborNode = universe.Nodes.FirstOrDefault(n => n.Id == neighborId);
                if (neighborNode == null) continue;

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
