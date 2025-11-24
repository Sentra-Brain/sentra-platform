using System;
using System.ComponentModel.DataAnnotations.Schema;
using Sentra.Domain.Enums;

namespace Sentra.Domain.Entities;

[Table("documents")]
public class DocumentEntity : BaseEntity
{
    public string Filename { get; set; }
    public string DisplayName { get; set; }
    public string? Description { get; set; }

    public DocumentFileType Filetype { get; set; }
    public string Path { get; set; }

    public DocumentStatus Status { get; set; } = DocumentStatus.Pending;
    public string? StatusMessage { get; set; }
    public string? Error { get; set; }
    public int? ChunksCount { get; set; }

    public string? MarkdownPath { get; set; }
    public int? MarkdownBytes { get; set; }
    public string? MarkdownHash { get; set; }
    public bool HasMarkdown { get; set; } = false;

    public Guid KnowledgeSourceId { get; set; }
    public Guid CreatedById { get; set; }
    public UserEntity CreatedBy { get; set; }
}
