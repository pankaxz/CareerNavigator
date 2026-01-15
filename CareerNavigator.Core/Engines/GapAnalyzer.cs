using CareerNavigator.Core.Models.DTOs;

namespace CareerNavigator.Core.Engines;

/// <summary>
/// Domain engine responsible for comparing User Profiles against Job Descriptions.
/// </summary>
public class GapAnalyzer
{
    private readonly IUniverseProvider _universeProvider;

    /// <summary>
    /// Initializes a new instance of the <see cref="GapAnalyzer"/> class.
    /// </summary>
    /// <param name="universeProvider">The singleton provider for accessing the graph universe.</param>
    public GapAnalyzer(IUniverseProvider universeProvider)
    {
        _universeProvider = universeProvider;
    }

    /// <summary>
    /// Performs a comprehensive gap analysis between a user profile and a target job.
    /// </summary>
    /// <remarks>
    /// The analysis involves three phases:
    /// <list type="number">
    /// <item><description><b>Direct Skills Gap:</b> Identifies skills explicitly required by the job but missing from the user.</description></item>
    /// <item><description><b>Implicit Dependency mapping:</b> Uses the `Universe` graph to find related skills (neighbors) that might bridge the gap.</description></item>
    /// <item><description><b>Seniority/Authority Scaling:</b> Compares the structural seniority (<c>Senior</c>, <c>Managerial</c>) of the roles.</description></item>
    /// </list>
    /// </remarks>
    /// <param name="user">The user's analyzed profile.</param>
    /// <param name="job">The job's analyzed requirements.</param>
    /// <returns>A detailed <see cref="GapAnalysisResult"/> highlighting missing skills and seniority mismatches.</returns>
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
            // Optimization: Use AdjacencyList for O(1) lookup
            if (universe.AdjacencyList.TryGetValue(missing, out var links))
            {
                foreach (var link in links)
                {
                    var neighbor = link.Source.Equals(missing, StringComparison.OrdinalIgnoreCase) ? link.Target : link.Source;

                    // If user has it, or it is already a known missing explicit skill, skip
                    if (user.Skills.Contains(neighbor, StringComparer.OrdinalIgnoreCase)) continue;
                    if (job.Skills.Contains(neighbor, StringComparer.OrdinalIgnoreCase)) continue;

                    implicitSkills.Add(neighbor);
                }
            }
        }
        result.ImplicitSkills = implicitSkills.ToList();

        // 3. Seniority/Authority Scaling
        bool isJobHighLevel = job.Level.Equals("Senior", StringComparison.OrdinalIgnoreCase) ||
                              job.Level.Equals("Managerial", StringComparison.OrdinalIgnoreCase);

        bool isUserHighLevel = user.Level.Equals("Senior", StringComparison.OrdinalIgnoreCase) ||
                               user.Level.Equals("Managerial", StringComparison.OrdinalIgnoreCase);

        if (isJobHighLevel && !isUserHighLevel)
        {
            result.SeniorityMismatch = true;
            result.Message = $"Role requires {job.Level} level, but your profile is rated as {user.Level}. Focus on demonstrating leadership and advanced system design.";
        }
        else
        {
            result.Message = "Your seniority level aligns with the role requirements.";
        }

        // Metadata Enrichment: The "Elite" Check
        if (isUserHighLevel)
        {
            // Optimization: Use NodeIndex for O(1) lookup
            int userEliteSkills = 0;
            foreach (var skill in user.Skills)
            {
                if (universe.NodeIndex.TryGetValue(skill, out var node) && node.IsSenior)
                {
                    userEliteSkills++;
                }
            }

            if (userEliteSkills == 0)
            {
                result.SeniorityMismatch = true;
                result.Message += " Note: You are targeting a Senior role or claim Senior experience, but your detected skills are primarily foundational. Consider acquiring specialized, high-authority skills.";
            }
        }

        return result;
    }
}
