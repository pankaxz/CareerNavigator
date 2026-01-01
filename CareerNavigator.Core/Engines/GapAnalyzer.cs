using CareerNavigator.Core.Models.DTOs;

namespace CareerNavigator.Core.Engines;

public class GapAnalyzer
{
    private readonly IUniverseProvider _universeProvider;

    public GapAnalyzer(IUniverseProvider universeProvider)
    {
        _universeProvider = universeProvider;
    }

    public GapAnalysisResult AnalyzeGap(AnalysisResult user, AnalysisResult job)
    {
        var result = new GapAnalysisResult();
        var universe = _universeProvider.GetUniverse();

        // 1. Direct Gap Identification
        var missingSkills = job.Skills.Except(user.Skills, StringComparer.OrdinalIgnoreCase).ToList();
        result.MissingSkills = missingSkills;

        // 2. Implicit Dependency Mapping
        var implicitSkills = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        foreach (var missing in missingSkills)
        {
            // Find neighbors of the missing skill in the target set
            // If the JD requires "Next.js" (which is missing) and it's linked to "TypeScript", 
            // and the user also lacks "TypeScript", flag it.

            // Logic: For any skill in TargetSkills that user doesn't have, check its neighbors.

            var links = universe.Links.Where(l =>
                l.Source.Equals(missing, StringComparison.OrdinalIgnoreCase) ||
                l.Target.Equals(missing, StringComparison.OrdinalIgnoreCase));

            foreach (var link in links)
            {
                var neighbor = link.Source.Equals(missing, StringComparison.OrdinalIgnoreCase) ? link.Target : link.Source;

                // If the user already has the neighbor, it's not a gap.
                if (user.Skills.Contains(neighbor, StringComparer.OrdinalIgnoreCase)) continue;

                // If the neighbor is already in the missing list, it's explicitly required, so strictly speaking not "implicit" but still a gap.
                // However, the requirement says "flag... as an implicit requirement even if the JD didn't mention it".
                // So if it's NOT in Job.Skills, but IS a strong neighbor of a missing Job Skill, recommend it.

                if (job.Skills.Contains(neighbor, StringComparer.OrdinalIgnoreCase)) continue; // It's explicit, not implicit.

                // Threshold check? The prompt says "90% linked". 
                // Our Link.Value is an int. Let's assume Value corresponds to strength. 
                // For now, we'll take any strong link (e.g. > 5? or just existence?).
                // Let's assume existence in the universe implies a strong enough link for now, 
                // or we can filter by link.Value if we knew the scale. 

                implicitSkills.Add(neighbor);
            }
        }
        result.ImplicitSkills = implicitSkills.ToList();

        // 3. Seniority/Authority Scaling
        // Check for Seniority Mismatch
        bool isJobSenior = job.Level.Equals("Senior", StringComparison.OrdinalIgnoreCase);
        bool isUserSenior = user.Level.Equals("Senior", StringComparison.OrdinalIgnoreCase);

        if (isJobSenior && !isUserSenior)
        {
            result.SeniorityMismatch = true;
            result.Message = $"Role requires Senior level, but your profile is rated as {user.Level}. Focus on demonstrating leadership and advanced system design.";
        }
        else
        {
            result.Message = "Your seniority level aligns with the role requirements.";
        }

        // Metadata Enrichment: The "Elite" Check
        // "If a user possesses skills that the DataFactory has flagged as IsSenior: true ... user's SkillSeniorityScore increases."
        // This part of the logic seems to belong to the UserAnalysis phase (generating the score), 
        // but here we are comparing. 
        // The prompt says: "If a user claims to be 'Senior' (Pass 2) but only possesses 'Junior' skills (Pass 1/3), the system identifies a Seniority Mismatch."

        // We can double check the user's claimed level vs their "Elite" skills count.
        if (isUserSenior)
        {
            var userEliteSkills = universe.Nodes
                .Where(n => user.Skills.Contains(n.Id, StringComparer.OrdinalIgnoreCase) && n.IsSenior)
                .Count();

            if (userEliteSkills == 0)
            {
                result.SeniorityMismatch = true;
                result.Message += " Note: You are targeting a Senior role or claim Senior experience, but your detected skills are primarily foundational. Consider acquiring specialized, high-authority skills.";
            }
        }

        return result;
    }
}
