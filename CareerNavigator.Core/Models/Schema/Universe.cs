namespace CareerNavigator.Core.Models.Schema;

public class Universe
{
    public List<Node> Nodes { get; set; } = new();
    public List<Link> Links { get; set; } = new();
}