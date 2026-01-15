using Moq;
using Xunit;
using CareerNavigator.Core.Engines;
using CareerNavigator.Core.Models.Schema;
using CareerNavigator.Core.Models.DTOs;

namespace CareerNavigator.Tests.Engines;

public class BridgeEngineTests
{
    private readonly Mock<IUniverseProvider> _universeProviderMock;
    private readonly BridgeEngine _engine;
    private readonly Universe _mockUniverse;

    public BridgeEngineTests()
    {
        _universeProviderMock = new Mock<IUniverseProvider>();
        _mockUniverse = new Universe();

        // Setup mock data
        var nodes = new List<Node>
        {
            new Node { Id = "Python", Group = "Skill" },
            new Node { Id = "Machine Learning", Group = "Skill", IsSenior = true },
            new Node { Id = "Django", Group = "Skill" }
        };
        _mockUniverse.Nodes = nodes;

        var links = new List<Link>
        {
            new Link { Source = "Python", Target = "Machine Learning", Value = 10 }, // Strong link
            new Link { Source = "Python", Target = "Django", Value = 5 }
        };
        _mockUniverse.Links = links;

        // Manual Index Population (Simulating UniverseProvider)
        _mockUniverse.NodeIndex = nodes.ToDictionary(n => n.Id, StringComparer.OrdinalIgnoreCase);

        // Bidirectional Adjacency List
        _mockUniverse.AdjacencyList = new Dictionary<string, List<Link>>(StringComparer.OrdinalIgnoreCase);
        foreach (var link in links)
        {
            if (!_mockUniverse.AdjacencyList.ContainsKey(link.Source)) _mockUniverse.AdjacencyList[link.Source] = new List<Link>();
            _mockUniverse.AdjacencyList[link.Source].Add(link);

            if (!_mockUniverse.AdjacencyList.ContainsKey(link.Target)) _mockUniverse.AdjacencyList[link.Target] = new List<Link>();
            _mockUniverse.AdjacencyList[link.Target].Add(link);
        }

        _universeProviderMock.Setup(p => p.GetUniverse()).Returns(_mockUniverse);
        _engine = new BridgeEngine(_universeProviderMock.Object);
    }

    [Fact]
    public void SuggestBridges_ShouldReturnConnectedSkills()
    {
        // Arrange
        var profile = new AnalysisResult
        {
            Skills = new List<string> { "Python" },
            Level = "Junior"
        };

        // Act
        var result = _engine.SuggestBridges(profile);

        // Assert
        Assert.Contains("Machine Learning", result);
        Assert.Contains("Django", result);
    }

    [Fact]
    public void SuggestBridges_ShouldPrioritizeSeniorSkills_ForJuniorProfile()
    {
        // "Machine Learning" is Senior and linked to "Python". Link Value 10 * 1.5 = 15.
        // "Django" is not Senior. Link Value 5.
        // Expect "Machine Learning" to be top.

        var profile = new AnalysisResult
        {
            Skills = new List<string> { "Python" },
            Level = "Junior"
        };

        var result = _engine.SuggestBridges(profile);

        Assert.Equal("Machine Learning", result.First());
    }
}
