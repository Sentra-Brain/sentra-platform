using Kommand.Abstractions;
using Sentra.Api.Features.Users.Queries;
using Sentra.Application.Users;

namespace Sentra.Api.Features.Users.Handlers;

/// <summary>
/// Handles retrieving a user's display name by ID.
/// </summary>
public sealed class GetUserDisplayNameQueryHandler : IQueryHandler<GetUserDisplayNameQuery, string>
{
    private readonly IUserRepository _users;
    private readonly ILogger<GetUserDisplayNameQueryHandler> _log;

    public GetUserDisplayNameQueryHandler(
        IUserRepository users,
        ILogger<GetUserDisplayNameQueryHandler> log)
    {
        _users = users;
        _log = log;
    }

    public async Task<string> HandleAsync(GetUserDisplayNameQuery query, CancellationToken ct)
    {
        var user = await _users.GetById(query.UserId);

        if (user is null)
        {
            _log.LogWarning("User not found for display name: {UserId}", query.UserId);
            return "Unknown User";
        }

        return user.FullName ?? user.Username;
    }
}
