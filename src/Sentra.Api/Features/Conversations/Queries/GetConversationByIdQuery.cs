using System;
using Kommand.Abstractions;
using Sentra.Api.Features.Conversations;

namespace Sentra.Api.Features.Conversations.Queries;

public sealed record GetConversationByIdQuery(
    Guid ConversationId,
    Guid UserId
) : IQuery<ConversationResponse>;
