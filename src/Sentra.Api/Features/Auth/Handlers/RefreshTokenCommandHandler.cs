using Kommand.Abstractions;
using Microsoft.EntityFrameworkCore;
using Sentra.Api.Features.Auth.Commands;
using Sentra.Application.Auth;
using Sentra.Infrastructure.Sql;

namespace Sentra.Api.Features.Auth.Handlers;

/// <summary>
/// Handles refresh token validation and new access token generation.
/// </summary>
public sealed class RefreshTokenCommandHandler : ICommandHandler<RefreshTokenCommand, RefreshTokenResponse>
{
    private readonly SentraDbContext _db;
    private readonly IJwtProvider _jwt;
    private readonly ILogger<RefreshTokenCommandHandler> _log;

    public RefreshTokenCommandHandler(
        SentraDbContext db,
        IJwtProvider jwt,
        ILogger<RefreshTokenCommandHandler> log)
    {
        _db = db;
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
        var normalizedUsername = tokenData.Username.ToLowerInvariant();
        var user = await _db.Users
            .Where(u => u.DeletedAt == null)
            .Where(u => u.Username.ToLower() == normalizedUsername || u.Email.ToLower() == normalizedUsername)
            .FirstOrDefaultAsync(ct);

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
