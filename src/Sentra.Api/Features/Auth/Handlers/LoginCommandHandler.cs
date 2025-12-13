using Kommand.Abstractions;
using Microsoft.AspNetCore.Identity;
using Sentra.Api.Features.Auth.Commands;
using Sentra.Application.Auth;
using Sentra.Application.Users;
using Sentra.Domain.Entities;

namespace Sentra.Api.Features.Auth.Handlers;

/// <summary>
/// Handles user login authentication and token generation.
/// </summary>
public sealed class LoginCommandHandler : ICommandHandler<LoginCommand, LoginResponse>
{
    private readonly IUserRepository _users;
    private readonly IPasswordHasher<User> _passwordHasher;
    private readonly IJwtProvider _jwt;
    private readonly ILogger<LoginCommandHandler> _log;

    public LoginCommandHandler(
        IUserRepository users,
        IPasswordHasher<User> hasher,
        IJwtProvider jwt,
        ILogger<LoginCommandHandler> log)
    {
        _users = users;
        _passwordHasher = hasher;
        _jwt = jwt;
        _log = log;
    }

    public async Task<LoginResponse> HandleAsync(LoginCommand command, CancellationToken ct)
    {
        // Find user by username or email
        var user = await _users.GetByUsername(command.EmailOrUsername)
                   ?? await _users.GetByEmail(command.EmailOrUsername.ToLowerInvariant());

        if (user is null || user.Disabled)
        {
            _log.LogWarning("Login attempt failed for {EmailOrUsername}", command.EmailOrUsername);
            throw new UnauthorizedAccessException("Invalid credentials");
        }

        // Verify password
        var verification = _passwordHasher.VerifyHashedPassword(
            user,
            user.HashedPassword,
            command.Password
        );

        if (verification == PasswordVerificationResult.Failed)
        {
            _log.LogWarning("Invalid password for user {Username}", user.Username);
            throw new UnauthorizedAccessException("Invalid credentials");
        }

        // Generate tokens
        var accessToken = _jwt.CreateAccessToken(
            user.Username,
            user.Roles,
            TimeSpan.FromMinutes(30)
        );

        var refreshToken = _jwt.CreateRefreshToken(
            user.Username,
            user.Roles,
            TimeSpan.FromDays(7)
        );

        _log.LogInformation("User {Username} logged in successfully", user.Username);

        return new LoginResponse(accessToken, refreshToken);
    }
}
