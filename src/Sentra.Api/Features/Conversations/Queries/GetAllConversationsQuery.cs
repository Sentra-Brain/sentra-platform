using System;
using System.Collections.Generic;
using Kommand.Abstractions;
using Sentra.Api.Features.Conversations;

namespace Sentra.Api.Features.Conversations.Queries;

public sealed record GetAllConversationsQuery(
    Guid UserId
) : IQuery<List<ConversationListItemResponse>>;
