using Kommand.Abstractions;
using Sentra.Api.Features.Users.Queries;
using Sentra.Application.Users;
using Sentra.Contracts.Users;

namespace Sentra.Api.Features.Users.Handlers;

/// <summary>
/// Handles retrieving the current authenticated user's information.
/// </summary>
public sealed class GetMeQueryHandler : IQueryHandler<GetMeQuery, UserResponse>
{
    private readonly IUserRepository _users;
    private readonly ILogger<GetMeQueryHandler> _log;

    public GetMeQueryHandler(
        IUserRepository users,
        ILogger<GetMeQueryHandler> log)
    {
        _users = users;
        _log = log;
    }

    public async Task<UserResponse> HandleAsync(GetMeQuery query, CancellationToken ct)
    {
        var user = await _users.GetById(query.UserId);

        if (user is null)
        {
            _log.LogWarning("User not found: {UserId}", query.UserId);
            throw new InvalidOperationException("User not found");
        }

        return new UserResponse(
            user.Id,
            user.Username,
            user.Email,
            user.FullName,
            user.Disabled,
            user.GetRoles().Select(r => r.ToString()).ToList()
        );
    }
}
