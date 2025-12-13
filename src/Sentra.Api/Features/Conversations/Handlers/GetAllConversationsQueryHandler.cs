using Kommand.Abstractions;
using Microsoft.EntityFrameworkCore;
using Sentra.Api.Features.Conversations.Queries;
using Sentra.Infrastructure.Sql;

namespace Sentra.Api.Features.Conversations.Handlers;

public sealed class GetAllConversationsQueryHandler : IQueryHandler<GetAllConversationsQuery, List<ConversationListItemResponse>>
{
    private readonly SentraDbContext _db;

    public GetAllConversationsQueryHandler(SentraDbContext db)
    {
        _db = db;
    }

    public async Task<List<ConversationListItemResponse>> HandleAsync(GetAllConversationsQuery query, CancellationToken cancellationToken)
    {
        return await _db.Conversations
            .AsNoTracking()
            .Where(c => c.DeletedAt == null)
            .Where(c => c.CreatedById == query.UserId)
            .OrderByDescending(c => c.CreatedAt)
            .Select(ConversationListItemResponse.Projection)
            .ToListAsync(cancellationToken);
    }
}
