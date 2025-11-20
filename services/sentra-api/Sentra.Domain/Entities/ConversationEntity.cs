using System;
using System.ComponentModel.DataAnnotations.Schema;

namespace Sentra.Domain.Entities;

[Table("conversations")]
public class ConversationEntity : BaseEntity
{
    public string? Title { get; set; }
    public string? Description { get; set; }
    public string? InitialPrompt { get; set; }

    public Guid CreatedById { get; set; }
    public UserEntity CreatedBy { get; set; }
}
