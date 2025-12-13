using Kommand.Abstractions;
using Microsoft.EntityFrameworkCore;
using Sentra.Api.Features.Users.Queries;
using Sentra.Infrastructure.Sql;

namespace Sentra.Api.Features.Users.Handlers;

/// <summary>
/// Handles retrieving the current authenticated user's information.
/// </summary>
public sealed class GetMeQueryHandler : IQueryHandler<GetMeQuery, UserResponse>
{
    private readonly SentraDbContext _db;
    private readonly ILogger<GetMeQueryHandler> _log;

    public GetMeQueryHandler(
        SentraDbContext db,
        ILogger<GetMeQueryHandler> log)
    {
        _db = db;
        _log = log;
    }

    public async Task<UserResponse> HandleAsync(GetMeQuery query, CancellationToken ct)
    {
        var user = await _db.Users
            .AsNoTracking()
            .Where(u => u.DeletedAt == null)
            .Where(u => u.Id == query.UserId)
            .Select(UserResponse.Projection)
            .FirstOrDefaultAsync(ct);

        if (user is null)
        {
            _log.LogWarning("User not found: {UserId}", query.UserId);
            throw new InvalidOperationException("User not found");
        }

        return user;
    }
}
