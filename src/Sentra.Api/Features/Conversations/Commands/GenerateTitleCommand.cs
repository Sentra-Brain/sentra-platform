using System;
using Kommand.Abstractions;
using Sentra.Api.Features.Conversations;

namespace Sentra.Api.Features.Conversations.Commands;

public sealed record GenerateTitleCommand(
    Guid ConversationId,
    Guid UserId
) : ICommand<GenerateTitleResponse>;
