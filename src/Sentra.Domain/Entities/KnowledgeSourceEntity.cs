using System;
using System.ComponentModel.DataAnnotations.Schema;
using Sentra.Domain.Enums;

namespace Sentra.Domain.Entities;

[Table("knowledge_sources")]
public class KnowledgeSourceEntity : BaseEntity
{
    public string Name { get; set; }

    public KnowledgeSourceType Type { get; set; }
    public string? Path { get; set; }
    public string? Description { get; set; }

    public KnowledgeSourceVisibility Visibility { get; set; } = KnowledgeSourceVisibility.Private;
    public bool AutoIndex { get; set; } = false;

    public KnowledgeSourceStatus Status { get; set; } = KnowledgeSourceStatus.Active;

    [ForeignKey(nameof(CreatedBy))]
    public Guid CreatedById { get; set; }
    public UserEntity? CreatedBy { get; set; }
}
