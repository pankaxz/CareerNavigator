namespace CareerNavigator.Core.Models.DTOs;

public class UserProfile
{
    public List<string> Skills { get; set; } = new();
    public int YearsOfExperience { get; set; }
    public bool IsSenior { get; set; }
}
