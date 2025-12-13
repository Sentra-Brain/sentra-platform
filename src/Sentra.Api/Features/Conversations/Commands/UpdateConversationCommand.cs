using System;
using Kommand.Abstractions;
using Sentra.Api.Features.Conversations;

namespace Sentra.Api.Features.Conversations.Commands;

public sealed record UpdateConversationCommand(
    Guid ConversationId,
    Guid UserId,
    string? Title,
    string? Description
) : ICommand<UpdateConversationResponse>;
