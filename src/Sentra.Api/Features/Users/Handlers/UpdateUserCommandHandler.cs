using Kommand.Abstractions;
using Microsoft.AspNetCore.Identity;
using Sentra.Api.Features.Users.Commands;
using Sentra.Application.Users;
using Sentra.Contracts.Users;
using Sentra.Domain.Entities;

namespace Sentra.Api.Features.Users.Handlers;

/// <summary>
/// Handles updating another user (admin operation).
/// </summary>
public sealed class UpdateUserCommandHandler : ICommandHandler<UpdateUserCommand, UserResponse>
{
    private readonly IUserRepository _users;
    private readonly IPasswordHasher<User> _passwordHasher;
    private readonly ILogger<UpdateUserCommandHandler> _log;

    public UpdateUserCommandHandler(
        IUserRepository users,
        IPasswordHasher<User> passwordHasher,
        ILogger<UpdateUserCommandHandler> log)
    {
        _users = users;
        _passwordHasher = passwordHasher;
        _log = log;
    }

    public async Task<UserResponse> HandleAsync(UpdateUserCommand command, CancellationToken ct)
    {
        // TODO: Add permission check - verify CurrentUserId has Admin role

        var user = await _users.GetById(command.UserToUpdateId);

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

        await _users.Update(user);

        _log.LogInformation("User {UserId} updated by {CurrentUserId}", command.UserToUpdateId, command.CurrentUserId);

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
