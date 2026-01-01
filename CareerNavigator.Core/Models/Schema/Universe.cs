namespace CareerNavigator.Core.Models.Schema;

public class Universe
{
    public List<Node> Nodes { get; set; } = new();
    public List<Link> Links { get; set; } = new();

    // Performance Indices (Ignored during JSON serialization)
    [Newtonsoft.Json.JsonIgnore]
    public Dictionary<string, Node> NodeIndex { get; set; } = new();

    [Newtonsoft.Json.JsonIgnore]
    public Dictionary<string, List<Link>> AdjacencyList { get; set; } = new();
}