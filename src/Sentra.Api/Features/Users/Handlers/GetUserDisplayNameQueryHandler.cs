using Kommand.Abstractions;
using Microsoft.EntityFrameworkCore;
using Sentra.Api.Features.Users.Queries;
using Sentra.Infrastructure.Sql;

namespace Sentra.Api.Features.Users.Handlers;

/// <summary>
/// Handles retrieving a user's display name by ID.
/// </summary>
public sealed class GetUserDisplayNameQueryHandler : IQueryHandler<GetUserDisplayNameQuery, string>
{
    private readonly SentraDbContext _db;
    private readonly ILogger<GetUserDisplayNameQueryHandler> _log;

    public GetUserDisplayNameQueryHandler(
        SentraDbContext db,
        ILogger<GetUserDisplayNameQueryHandler> log)
    {
        _db = db;
        _log = log;
    }

    public async Task<string> HandleAsync(GetUserDisplayNameQuery query, CancellationToken ct)
    {
        var displayName = await _db.Users
            .AsNoTracking()
            .Where(u => u.DeletedAt == null)
            .Where(u => u.Id == query.UserId)
            .Select(u => u.FullName ?? u.Username)
            .FirstOrDefaultAsync(ct);

        if (displayName is null)
        {
            _log.LogWarning("User not found for display name: {UserId}", query.UserId);
            return "Unknown User";
        }

        return displayName;
    }
}
