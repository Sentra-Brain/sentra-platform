using Sentra.Domain.Enums;
using System.ComponentModel.DataAnnotations.Schema;

namespace Sentra.Domain.Entities;

[Table("users")]
public class User : Base
{
    public required string Username { get; set; }
    public required string Email { get; set; }
    public required string FullName { get; set; }
    public required string HashedPassword { get; set; }
    public bool Disabled { get; set; } = false;
    public required string Roles { get; set; }
    public string? JobTitle { get; set; }
    public string? AvatarUrl { get; set; }
    public string? PhoneNumber { get; set; }
    public string? Bio { get; set; }
    public string PreferredLanguage { get; set; } = "es";
    public string Timezone { get; set; } = "Europe/Madrid";

    public IList<Conversation> Conversations { get; set; } = new List<Conversation>();
    public IList<Document> Documents { get; set; } = new List<Document>();
    public IList<KnowledgeSource> KnowledgeSources { get; set; } = new List<KnowledgeSource>();

    public IEnumerable<Role> GetRoles()
    {
        foreach (var r in Roles.Split(',', StringSplitOptions.RemoveEmptyEntries))
            yield return Enum.Parse<Role>(r, true);
    }

    public void SetRoles(IEnumerable<Role> roles)
    {
        Roles = string.Join(",", roles);
    }
}
