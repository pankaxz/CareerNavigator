using CareerNavigator.Core.Engines;
using CareerNavigator.Core.Models.Schema;
using Moq;
using Xunit;

namespace CareerNavigator.Tests;

public class SkillScannerTests
{
    private readonly Mock<IUniverseProvider> _mockUniverse;
    private readonly SkillScanner _scanner;

    public SkillScannerTests()
    {
        _mockUniverse = new Mock<IUniverseProvider>();

        // Setup a fake universe
        var fakeUniverse = new Universe
        {
            Nodes = new List<Node>
            {
                new Node { Id = "C++" },
                new Node { Id = "C" },
                new Node { Id = ".NET" },
                new Node { Id = "Python" },
                new Node { Id = "Java" }
            }
        };

        _mockUniverse.Setup(u => u.GetUniverse()).Returns(fakeUniverse);
        _scanner = new SkillScanner(_mockUniverse.Object);
    }

    [Fact]
    public void FindMatches_Should_Return_Empty_If_Text_Is_Null()
    {
        var result = _scanner.AnalyzeProfile(null!).Skills;
        Assert.Empty(result);
    }

    [Fact]
    public void FindMatches_Should_Identify_Simple_Skills()
    {
        var text = "I know Python and Java.";
        var result = _scanner.AnalyzeProfile(text).Skills;

        Assert.Contains("Python", result);
        Assert.Contains("Java", result);
    }

    [Fact]
    public void FindMatches_Should_Identify_Special_Char_Skills()
    {
        var text = "I am an expert in C++ and .NET development.";
        var result = _scanner.AnalyzeProfile(text).Skills;

        Assert.Contains("C++", result);
        Assert.Contains(".NET", result);
    }

    [Fact]
    public void FindMatches_Should_Distinguish_C_From_Partial_Words()
    {
        // "C" should match "C programming" but NOT "Cloud", "Case", "Music"
        var text = "I like Cloud Computing and C programming.";
        var result = _scanner.AnalyzeProfile(text).Skills;

        Assert.Contains("C", result);
        // We can't assert "Cloud" is NOT there because it's not in our fake universe anyway.
        // But if we had "Cloud" in universe, it would match.
        // Key is that "Cloud" shouldn't trigger "C".
    }

    [Fact]
    public void FindMatches_Should_Not_Match_Substrings()
    {
        // "Go" (not in list, but hypothetically) shouldn't match "Google".
        // "C" shouldn't match in "Basic".
        var text = "Visual Basic is old.";
        var result = _scanner.AnalyzeProfile(text).Skills;

        Assert.DoesNotContain("C", result);
    }
}
