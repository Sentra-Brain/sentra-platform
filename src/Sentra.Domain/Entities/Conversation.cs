using System;
using System.ComponentModel.DataAnnotations.Schema;

namespace Sentra.Domain.Entities;

[Table("conversations")]
public class Conversation : Base
{
    public string? Title { get; set; }
    public string? Description { get; set; }
    public string? InitialPrompt { get; set; }

    [ForeignKey(nameof(CreatedBy))]
    public Guid CreatedById { get; set; }
    public User? CreatedBy { get; set; }
}
