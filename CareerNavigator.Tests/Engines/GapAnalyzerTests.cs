using CareerNavigator.Core.Engines;
using CareerNavigator.Core.Models.DTOs;
using CareerNavigator.Core.Models.Schema;
using Moq;
using Xunit;

namespace CareerNavigator.Tests.Engines;

public class GapAnalyzerTests
{
    private readonly Universe _mockUniverse;
    private readonly Mock<IUniverseProvider> _mockProvider;
    private readonly GapAnalyzer _analyzer;

    public GapAnalyzerTests()
    {
        _mockUniverse = new Universe
        {
            Nodes = new List<Node>
            {
                new Node { Id = "C#", IsSenior = false },
                new Node { Id = "TypeScript", IsSenior = false },
                new Node { Id = "React", IsSenior = false },
                new Node { Id = "Next.js", IsSenior = false },
                new Node { Id = "Azure", IsSenior = true },
                new Node { Id = "System Design", IsSenior = true }
            },
            Links = new List<Link>
            {
                // TypeScript <-> Next.js are neighbors
                new Link { Source = "TypeScript", Target = "Next.js", Value = 10 },
                new Link { Source = "C#", Target = "Azure", Value = 10 }
            }
        };

        _mockProvider = new Mock<IUniverseProvider>();
        _mockProvider.Setup(p => p.GetUniverse()).Returns(_mockUniverse);

        _analyzer = new GapAnalyzer(_mockProvider.Object);
    }

    [Fact]
    public void AnalyzeGap_IdentifiesDirectMissingSkills()
    {
        var user = new AnalysisResult { Skills = new List<string> { "C#", "SQL" } };
        var job = new AnalysisResult { Skills = new List<string> { "C#", "SQL", "Azure" } };

        var result = _analyzer.AnalyzeGap(user, job);

        Assert.Contains("Azure", result.MissingSkills);
        Assert.Single(result.MissingSkills);
    }

    [Fact]
    public void AnalyzeGap_IdentifiesImplicitDependencies()
    {
        // Job requires Next.js, User has nothing.
        // User is missing Next.js.
        // Next.js is linked to TypeScript.
        // GapAnalyzer should suggest TypeScript implicitly.

        var user = new AnalysisResult { Skills = new List<string> { "HTML" } };
        var job = new AnalysisResult { Skills = new List<string> { "Next.js" } };

        var result = _analyzer.AnalyzeGap(user, job);

        Assert.Contains("Next.js", result.MissingSkills);
        Assert.Contains("TypeScript", result.ImplicitSkills);
    }

    [Fact]
    public void AnalyzeGap_IdentifiesSeniorityMismatch()
    {
        var user = new AnalysisResult { Level = "Mid", Skills = new List<string> { "C#" } };
        var job = new AnalysisResult { Level = "Senior", Skills = new List<string> { "C#" } };

        var result = _analyzer.AnalyzeGap(user, job);

        Assert.True(result.SeniorityMismatch);
        Assert.Contains("Role requires Senior level", result.Message);
    }

    [Fact]
    public void AnalyzeGap_NoSeniorityMismatch_WhenAligned()
    {
        var user = new AnalysisResult { Level = "Senior", Skills = new List<string> { "C#", "System Design" } };
        var job = new AnalysisResult { Level = "Senior", Skills = new List<string> { "C#" } };

        var result = _analyzer.AnalyzeGap(user, job);

        Assert.False(result.SeniorityMismatch);
        Assert.Contains("aligns with the role", result.Message);
    }
}
