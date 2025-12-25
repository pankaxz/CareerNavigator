namespace CareerNavigator.Core.Models.Schema;
public class Node
{
    public string Id { get; set; } = "";
    public string Group { get; set; } = "";
    public int Val { get; set; }
    public double SeniorityScore { get; set; }
    public bool IsSenior { get; set; }
}
