namespace Sentra.Domain.Enums;

public enum DocumentStatus
{
    Pending,
    Processing,
    Extracting,
    Chunking,
    Embedding,
    Indexing,
    Indexed,
    Failed,
    ToBeRemoved,
    Removed
}
