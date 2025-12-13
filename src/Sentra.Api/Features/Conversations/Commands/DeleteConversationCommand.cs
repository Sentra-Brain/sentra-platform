using System;
using Kommand.Abstractions;
using Sentra.Api.Features.Conversations;

namespace Sentra.Api.Features.Conversations.Commands;

public sealed record DeleteConversationCommand(
    Guid ConversationId,
    Guid UserId
) : ICommand<DeleteConversationResponse>;
