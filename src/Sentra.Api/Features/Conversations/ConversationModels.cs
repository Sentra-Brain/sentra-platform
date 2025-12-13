using System.Linq.Expressions;

namespace Sentra.Api.Features.Conversations;

// Request/Response Models

public sealed record CreateConversationRequest(
    string InitialPrompt
);

public sealed record CreateConversationResponse(
    Guid Id,
    string Title,
    DateTime CreatedAt
);

public sealed record ConversationListItemResponse(
    Guid Id,
    string Title,
    DateTime CreatedAt
)
{
    /// <summary>
    /// Expression to project from Conversation entity to ConversationListItemResponse.
    /// </summary>
    public static Expression<Func<Domain.Entities.Conversation, ConversationListItemResponse>> Projection =>
        c => new ConversationListItemResponse(
            c.Id,
            c.Title ?? "Untitled",
            c.CreatedAt
        );
}

public sealed record ConversationResponse(
    Guid Id,
    string? Title,
    string? Description,
    string? InitialPrompt,
    DateTime CreatedAt,
    DateTime? UpdatedAt
)
{
    /// <summary>
    /// Expression to project from Conversation entity to ConversationResponse.
    /// </summary>
    public static Expression<Func<Domain.Entities.Conversation, ConversationResponse>> Projection =>
        c => new ConversationResponse(
            c.Id,
            c.Title,
            c.Description,
            c.InitialPrompt,
            c.CreatedAt,
            c.UpdatedAt
        );
}

public sealed record UpdateConversationRequest(
    string? Title,
    string? Description
);

public sealed record UpdateConversationResponse(
    Guid ConversationId,
    string? Title,
    string? Description
);

public sealed record DeleteConversationResponse(
    bool Success,
    string Message
);

public sealed record GenerateTitleResponse(
    Guid ConversationId,
    string Title
);
