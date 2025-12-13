using Kommand.Abstractions;
using Sentra.Api.Features.Auth.Commands;
using Sentra.Application.Auth;
using Sentra.Application.Users;

namespace Sentra.Api.Features.Auth.Handlers;

/// <summary>
/// Handles refresh token validation and new access token generation.
/// </summary>
public sealed class RefreshTokenCommandHandler : ICommandHandler<RefreshTokenCommand, RefreshTokenResponse>
{
    private readonly IUserRepository _users;
    private readonly IJwtProvider _jwt;
    private readonly ILogger<RefreshTokenCommandHandler> _log;

    public RefreshTokenCommandHandler(
        IUserRepository users,
        IJwtProvider jwt,
        ILogger<RefreshTokenCommandHandler> log)
    {
        _users = users;
        _jwt = jwt;
        _log = log;
    }

    public async Task<RefreshTokenResponse> HandleAsync(RefreshTokenCommand command, CancellationToken ct)
    {
        // Validate refresh token
        var tokenData = _jwt.ValidateToken(command.RefreshToken);

        if (tokenData.Username is null || !tokenData.IsRefreshToken)
        {
            _log.LogWarning("Invalid refresh token format");
            throw new UnauthorizedAccessException("Invalid refresh token");
        }

        // Find user
        var user = await _users.GetByUsername(tokenData.Username)
                   ?? await _users.GetByEmail(tokenData.Username.ToLowerInvariant());

        if (user is null || user.Disabled)
        {
            _log.LogWarning("Refresh token references invalid or disabled user: {Username}", tokenData.Username);
            throw new UnauthorizedAccessException("Invalid refresh token");
        }

        // Generate new access token
        var accessToken = _jwt.CreateAccessToken(
            user.Username,
            user.Roles,
            TimeSpan.FromMinutes(30)
        );

        _log.LogInformation("Access token refreshed for user {Username}", user.Username);

        return new RefreshTokenResponse(accessToken);
    }
}
