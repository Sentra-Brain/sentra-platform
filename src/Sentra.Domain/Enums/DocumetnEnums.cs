// File: Sentra.Domain/Enums/DocumentEnums.cs
namespace Sentra.Domain.Enums;

public enum DocumentFileType
{
    Pdf,
    Docx,
    Txt,
    Md,
    Html,
    Eml,
    Msg,
    Epub
}

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
