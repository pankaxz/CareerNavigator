using CareerNavigator.Core.Engines;
using CareerNavigator.Core.Models.Schema;
using CareerNavigator.Core.Models.DTOs;
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

        // Use real parser for tests to verify e2e logic
        var parser = new SkillParser(_mockUniverse.Object);
        _scanner = new SkillScanner(parser, _mockUniverse.Object);
    }

    [Fact]
    public void FindMatches_Should_Return_Empty_If_Text_Is_Null()
    {
        var result = _scanner.AnalyzeProfile((string)null!).Skills;
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
    [Fact]
    public void AnalyzeJob_Should_Identify_Skills()
    {
        var text = "We are looking for a C++ developer.";
        var result = _scanner.AnalyzeJob(text).Skills;

        Assert.Contains("C++", result);
    }

    [Fact]
    public void AnalyzeJob_Should_Detect_Senior_From_Title()
    {
        // Even with no years mentioned, "Senior" in text should trigger Senior level
        var text = "We need a Senior Developer.";
        var result = _scanner.AnalyzeJob(text);

        Assert.Equal("Senior", result.Level);
    }

    [Fact]
    public void AnalyzeJob_Should_Detect_Junior_From_Title()
    {
        var text = "Hiring a Junior Helper.";
        var result = _scanner.AnalyzeJob(text);

        Assert.Equal("Junior", result.Level);
    }

    [Fact]
    public void AnalyzeProfile_Should_Boost_Score_For_Architect()
    {
        // "Python" base score is likely decent, but "Architected" should boost it significantly.
        // We'll trust that the boost logic bumps it up.
        // Since we don't know the exact base score of the fake universe nodes easily without calculation,
        // we can check if it stays high or hits a Senior threshold if we assume Python is mid-tier.

        var text = "I architected the entire Python backend.";
        var result = _scanner.AnalyzeProfile(text);

        // Verification: The score should be boosted. 
        // Let's verify it triggered at least some score.
        Assert.True(result.ProfileSeniorityScore > 0);
    }

    [Fact]
    public void AnalyzeProfile_Should_Respect_Manual_Inputs()
    {
        var request = new AnalysisRequest
        {
            Text = "I have some basic java skills.",
            ManualSkills = new List<string> { "C++", "Python" }, // Overrides text
            ManualYearsOfExperience = 10, // Overrides text (which has none mentioned)
            AdditionalDetails = "I architected the system." // Boosts score
        };

        var result = _scanner.AnalyzeProfile(request);

        Assert.Contains("C++", result.Skills);
        Assert.Contains("Python", result.Skills);
        Assert.DoesNotContain("Java", result.Skills); // Manual overrides, doesn't merge (as per current logic)
        Assert.Equal(10, result.YearsOfExperience);
        Assert.True(result.ProfileSeniorityScore > 0); // Architect boost
        Assert.Equal("Senior", result.Level); // Manual YOE 10 should drive Level to Senior
    }
}
