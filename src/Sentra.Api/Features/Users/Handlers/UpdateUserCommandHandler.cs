using Kommand.Abstractions;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using Sentra.Api.Features.Users.Commands;
using Sentra.Domain.Entities;
using Sentra.Infrastructure.Sql;

namespace Sentra.Api.Features.Users.Handlers;

/// <summary>
/// Handles updating another user (admin operation).
/// </summary>
public sealed class UpdateUserCommandHandler : ICommandHandler<UpdateUserCommand, UserResponse>
{
    private readonly SentraDbContext _db;
    private readonly IPasswordHasher<User> _passwordHasher;
    private readonly ILogger<UpdateUserCommandHandler> _log;

    public UpdateUserCommandHandler(
        SentraDbContext db,
        IPasswordHasher<User> passwordHasher,
        ILogger<UpdateUserCommandHandler> log)
    {
        _db = db;
        _passwordHasher = passwordHasher;
        _log = log;
    }

    public async Task<UserResponse> HandleAsync(UpdateUserCommand command, CancellationToken ct)
    {
        // TODO: Add permission check - verify CurrentUserId has Admin role

        var user = await _db.Users
            .Where(u => u.DeletedAt == null)
            .Where(u => u.Id == command.UserToUpdateId)
            .FirstOrDefaultAsync(ct);

        if (user is null)
        {
            _log.LogWarning("User not found for update: {UserId}", command.UserToUpdateId);
            throw new InvalidOperationException($"User {command.UserToUpdateId} not found");
        }

        // Update password if provided
        if (!string.IsNullOrWhiteSpace(command.Password))
        {
            user.HashedPassword = _passwordHasher.HashPassword(user, command.Password);
        }

        await _db.SaveChangesAsync(ct);

        _log.LogInformation("User {UserId} updated by {CurrentUserId}", command.UserToUpdateId, command.CurrentUserId);

        // Re-query using projection
        return await _db.Users
            .Where(u => u.Id == user.Id)
            .Select(UserResponse.Projection)
            .FirstAsync(ct);
    }
}
