using System.Text.RegularExpressions;
using CareerNavigator.Core.Models.DTOs;
using CareerNavigator.Core.Models.Schema;

namespace CareerNavigator.Core.Engines.Strategies;

public class JobDescriptionAnalysisStrategy : BaseAnalysisStrategy
{
    protected override string DetermineLevel(int years, double score, string text)
    {
        // Explicit Override: Check for Title Keywords

        // "Manager", "Director", "Head", "VP", "Chief" -> Managerial
        if (text.Contains("manager") || text.Contains("director") || text.Contains("head of") || text.Contains("vp") || text.Contains("chief") || text.Contains("leadership"))
        {
            return "Managerial";
        }

        // "Senior", "Lead", "Principal", "Architect", "Staff" -> Senior
        if (text.Contains("senior") || text.Contains("lead") || text.Contains("principal") || text.Contains("architect") || text.Contains("staff"))
        {
            return "Senior";
        }

        // "Junior", "Entry", "Intern", "Associate" -> Junior
        if (text.Contains("junior") || text.Contains("entry level") || text.Contains("intern"))
        {
            return "Junior";
        }

        // Fallback to base logic
        return base.DetermineLevel(years, score, text);
    }


}
