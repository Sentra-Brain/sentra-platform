using System.ComponentModel.DataAnnotations.Schema;

namespace Sentra.Domain.Entities;

[Table("organizations")]
public class OrganizationEntity : BaseEntity
{
    public string Name { get; set; }
    public string Slug { get; set; }
    public string? Description { get; set; }
    public string? Location { get; set; }
    public string? ContactEmail { get; set; }
}
