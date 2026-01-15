using CareerNavigator.Core.Models.Schema;

namespace CareerNavigator.Core.Engines;

public interface IUniverseProvider
{
    Universe GetUniverse();
    List<string> GetNeighbors(string nodeId);
    List<string> GetShortestPath(string startId, string endId);
}
