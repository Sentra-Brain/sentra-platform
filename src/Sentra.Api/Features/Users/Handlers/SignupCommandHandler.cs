using Kommand.Abstractions;
using Microsoft.AspNetCore.Identity;
using Sentra.Api.Features.Users.Commands;
using Sentra.Application.Users;
using Sentra.Contracts.Users;
using Sentra.Domain.Entities;

namespace Sentra.Api.Features.Users.Handlers;

/// <summary>
/// Handles user signup registration.
/// </summary>
public sealed class SignupCommandHandler : ICommandHandler<SignupCommand, SignupResponse>
{
    private readonly IUserRepository _users;
    private readonly IPasswordHasher<User> _passwordHasher;
    private readonly ILogger<SignupCommandHandler> _log;

    public SignupCommandHandler(
        IUserRepository users,
        IPasswordHasher<User> passwordHasher,
        ILogger<SignupCommandHandler> log)
    {
        _users = users;
        _passwordHasher = passwordHasher;
        _log = log;
    }

    public async Task<SignupResponse> HandleAsync(SignupCommand command, CancellationToken ct)
    {
        // Check if username already exists
        var existingUser = await _users.GetByUsername(command.Username);
        if (existingUser is not null)
        {
            _log.LogWarning("Signup attempt with existing username: {Username}", command.Username);
            throw new InvalidOperationException($"Username '{command.Username}' is already taken");
        }

        // Check if email already exists
        var existingEmail = await _users.GetByEmail(command.Email.ToLowerInvariant());
        if (existingEmail is not null)
        {
            _log.LogWarning("Signup attempt with existing email: {Email}", command.Email);
            throw new InvalidOperationException($"Email '{command.Email}' is already registered");
        }

        // Create new user
        var user = new User
        {
            Id = Guid.NewGuid(),
            Username = command.Username,
            Email = command.Email.ToLowerInvariant(),
            FullName = command.FullName,
            HashedPassword = _passwordHasher.HashPassword(null!, command.Password),
            Disabled = false, // In Python API, they send email verification. Here we enable immediately.
            Roles = "User", // Default role (comma-separated string)
            CreatedAt = DateTime.UtcNow,
            PreferredLanguage = "en",
            Timezone = "UTC"
        };

        await _users.Add(user);

        _log.LogInformation("User {Username} registered successfully", user.Username);

        var userResponse = new UserResponse(
            user.Id,
            user.Username,
            user.Email,
            user.FullName,
            user.Disabled,
            user.GetRoles().Select(r => r.ToString()).ToList()
        );

        return new SignupResponse(
            userResponse,
            "Your account has been created successfully. You can now log in."
        );
    }
}
