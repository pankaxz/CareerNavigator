namespace CareerNavigator.Core.Models.Schema;

public class Link
{
    public string Source { get; set; } = "";
    public string Target { get; set; } = "";
    public int Value { get; set; } = 0;
    public float SeniorityScore { get; set; } = 0;
    public bool IsSenior { get; set; } = false;
}            
