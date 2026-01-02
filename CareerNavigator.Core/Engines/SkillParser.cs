using System.Text;
using CareerNavigator.Core.Models.Schema;

namespace CareerNavigator.Core.Engines;

public class SkillParser
{
    private readonly IUniverseProvider _universeProvider;
    private readonly ILogger<SkillParser> _logger;

    public SkillParser(IUniverseProvider universeProvider, ILogger<SkillParser> logger)
    {
        _universeProvider = universeProvider;
        _logger = logger;
    }

    public List<string> ParseSkills(string text)
    {
        if (string.IsNullOrWhiteSpace(text)) return new List<string>();

        HashSet<string> matchedIds = new(StringComparer.OrdinalIgnoreCase);
        Universe universe = _universeProvider.GetUniverse();
        int maxPhraseLength = universe.MaxSkillPhraseLength;

        // 1. Breake the JD/Resume into individual words
        List<string> tokens = Tokenize(text);
        Console.WriteLine($"Tokens: {string.Join(", ", tokens)} Count: {tokens.Count}");

        // 2. N-Gram Greedy Lookup
        for (int i = 0; i < tokens.Count;)
        {
            bool matched = false;
            // Try longest phrases first (Greedy)
            int maxCheck = Math.Min(maxPhraseLength, tokens.Count - i);

            for (int len = maxCheck; len >= 1; len--)
            {
                string phrase = GetPhrase(tokens, i, len);

                // O(1) Lookup
                if (universe.NodeIndex.ContainsKey(phrase))
                {
                    matchedIds.Add(universe.NodeIndex[phrase].Id);
                    i += len; // Consume tokens
                    matched = true;
                    break;
                }
            }

            if (!matched)
            {
                i++;
            }
        }

        return matchedIds.ToList();
    }

    private List<string> Tokenize(string text)
    {
        // Split by whitespace
        var rawTokens = text.Split(new[] { ' ', '\r', '\n', '\t' }, StringSplitOptions.RemoveEmptyEntries);
        var cleanTokens = new List<string>(rawTokens.Length);

        // Standard punctuation to strip, BUT keep:
        // '.' for tokens starting with it (.NET) or inside it (Node.js)
        // '+' (C++)
        // '#' (C#)
        char[] trimChars = { ',', ';', ':', '!', '?', '(', ')', '[', ']', '{', '}', '"', '\'', '/', '\\' };

        foreach (var t in rawTokens)
        {
            var token = t.Trim(trimChars);

            // Only trim trailing dot (sentence end), not leading dot (.NET)
            if (token.EndsWith("."))
            {
                token = token.TrimEnd('.');
            }

            if (token.Length > 0)
            {
                cleanTokens.Add(token);
            }
        }
        return cleanTokens;
    }

    private string GetPhrase(List<string> tokens, int start, int length)
    {
        if (length == 1) return tokens[start];

        // Optimization: Avoid LINQ Skip() which is O(start).
        // Use StringBuilder for O(length) speed.
        var sb = new StringBuilder();
        for (int i = 0; i < length; i++)
        {
            if (i > 0) sb.Append(' ');
            sb.Append(tokens[start + i]);
        }
        return sb.ToString();
    }
}
