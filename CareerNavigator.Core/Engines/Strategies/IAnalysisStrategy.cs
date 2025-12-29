using CareerNavigator.Core.Models.DTOs;

namespace CareerNavigator.Core.Engines.Strategies;

public interface IAnalysisStrategy
{
    AnalysisResult Analyze(AnalysisRequest request, List<string> skillIds, IUniverseProvider universeProvider);
}
