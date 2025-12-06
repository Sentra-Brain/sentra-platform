using Microsoft.Extensions.Logging;
using Microsoft.AspNetCore.Identity;
using Sentra.Application.Users;
using Sentra.Domain.Entities;

namespace Sentra.Application.Auth;

public sealed class AuthService : IAuthService
{
    private readonly IUserRepository _users;
    private readonly IPasswordHasher<User> _passwordHasher;
    private readonly IJwtProvider _jwt;
    private readonly ILogger<AuthService> _log;

    public AuthService(
        IUserRepository users,
        IPasswordHasher<User> hasher,
        IJwtProvider jwt,
        ILogger<AuthService> log)
    {
        _users = users;
        _passwordHasher = hasher;
        _jwt = jwt;
        _log = log;
    }

    public async Task<LoginResult> Login(string username, string password)
    {
        var user = await _users.GetByUsername(username)
                   ?? await _users.GetByEmail(username.ToLower());

        if (user is null || user.Disabled)
            throw new UnauthorizedAccessException("Invalid credentials");

        var verification = _passwordHasher.VerifyHashedPassword(
            user,
            user.HashedPassword,
            password
        );

        if (verification == PasswordVerificationResult.Failed)
            throw new UnauthorizedAccessException("Invalid credentials");

        var access = _jwt.CreateAccessToken(user.Username, user.Roles, TimeSpan.FromMinutes(30));
        var refresh = _jwt.CreateRefreshToken(user.Username, user.Roles, TimeSpan.FromDays(7));

        return new LoginResult(access, refresh);
    }

    public async Task<AccessTokenResult> Refresh(string refreshToken)
    {
        var data = _jwt.ValidateToken(refreshToken);

        if (data.Username is null || !data.IsRefreshToken)
            throw new UnauthorizedAccessException("Invalid refresh token");

        var user = await _users.GetByUsername(data.Username)
                   ?? await _users.GetByEmail(data.Username.ToLower());

        if (user is null || user.Disabled)
            throw new UnauthorizedAccessException("Invalid refresh token");

        var access = _jwt.CreateAccessToken(user.Username, user.Roles, TimeSpan.FromMinutes(30));

        return new AccessTokenResult(access);
    }
}
