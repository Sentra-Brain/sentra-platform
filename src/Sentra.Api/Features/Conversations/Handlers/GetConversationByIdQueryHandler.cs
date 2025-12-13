using Kommand.Abstractions;
using Microsoft.EntityFrameworkCore;
using Sentra.Api.Features.Conversations.Queries;
using Sentra.Infrastructure.Sql;

namespace Sentra.Api.Features.Conversations.Handlers;

public sealed class GetConversationByIdQueryHandler : IQueryHandler<GetConversationByIdQuery, ConversationResponse>
{
    private readonly SentraDbContext _db;

    public GetConversationByIdQueryHandler(SentraDbContext db)
    {
        _db = db;
    }

    public async Task<ConversationResponse> HandleAsync(GetConversationByIdQuery query, CancellationToken cancellationToken)
    {
        var conversation = await _db.Conversations
            .AsNoTracking()
            .Where(c => c.DeletedAt == null)
            .Where(c => c.Id == query.ConversationId)
            .Where(c => c.CreatedById == query.UserId)
            .Select(ConversationResponse.Projection)
            .FirstOrDefaultAsync(cancellationToken);

        if (conversation == null)
        {
            throw new InvalidOperationException("Conversation not found");
        }

        return conversation;
    }
}
