using Kommand.Abstractions;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using Sentra.Api.Features.Users.Commands;
using Sentra.Domain.Entities;
using Sentra.Infrastructure.Sql;

namespace Sentra.Api.Features.Users.Handlers;

/// <summary>
/// Handles user signup registration.
/// </summary>
public sealed class SignupCommandHandler : ICommandHandler<SignupCommand, SignupResponse>
{
    private readonly SentraDbContext _db;
    private readonly IPasswordHasher<User> _passwordHasher;
    private readonly ILogger<SignupCommandHandler> _log;

    public SignupCommandHandler(
        SentraDbContext db,
        IPasswordHasher<User> passwordHasher,
        ILogger<SignupCommandHandler> log)
    {
        _db = db;
        _passwordHasher = passwordHasher;
        _log = log;
    }

    public async Task<SignupResponse> HandleAsync(SignupCommand command, CancellationToken ct)
    {
        // Check if username already exists
        var usernameExists = await _db.Users
            .Where(u => u.DeletedAt == null)
            .AnyAsync(u => u.Username.ToLower() == command.Username.ToLower(), ct);
        
        if (usernameExists)
        {
            _log.LogWarning("Signup attempt with existing username: {Username}", command.Username);
            throw new InvalidOperationException($"Username '{command.Username}' is already taken");
        }

        // Check if email already exists
        var normalizedEmail = command.Email.ToLowerInvariant();
        var emailExists = await _db.Users
            .Where(u => u.DeletedAt == null)
            .AnyAsync(u => u.Email.ToLower() == normalizedEmail, ct);
        
        if (emailExists)
        {
            _log.LogWarning("Signup attempt with existing email: {Email}", command.Email);
            throw new InvalidOperationException($"Email '{command.Email}' is already registered");
        }

        // Create new user
        var user = new User
        {
            Id = Guid.NewGuid(),
            Username = command.Username,
            Email = normalizedEmail,
            FullName = command.FullName,
            HashedPassword = _passwordHasher.HashPassword(null!, command.Password),
            Disabled = false, // In Python API, they send email verification. Here we enable immediately.
            Roles = "User", // Default role (comma-separated string)
            CreatedAt = DateTime.UtcNow,
            PreferredLanguage = "en",
            Timezone = "UTC"
        };

        _db.Users.Add(user);
        await _db.SaveChangesAsync(ct);

        _log.LogInformation("User {Username} registered successfully", user.Username);

        // Re-query using projection
        var userResponse = await _db.Users
            .Where(u => u.Id == user.Id)
            .Select(UserResponse.Projection)
            .FirstAsync(ct);

        return new SignupResponse(userResponse, "User registered successfully");
    }
}
