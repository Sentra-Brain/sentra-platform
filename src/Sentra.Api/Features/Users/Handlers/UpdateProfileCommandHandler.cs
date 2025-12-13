using Kommand.Abstractions;
using Sentra.Api.Features.Users.Commands;
using Sentra.Application.Users;
using Sentra.Contracts.Users;

namespace Sentra.Api.Features.Users.Handlers;

/// <summary>
/// Handles updating the current user's profile information.
/// </summary>
public sealed class UpdateProfileCommandHandler : ICommandHandler<UpdateProfileCommand, UserProfileResponse>
{
    private readonly IUserRepository _users;
    private readonly ILogger<UpdateProfileCommandHandler> _log;

    public UpdateProfileCommandHandler(
        IUserRepository users,
        ILogger<UpdateProfileCommandHandler> log)
    {
        _users = users;
        _log = log;
    }

    public async Task<UserProfileResponse> HandleAsync(UpdateProfileCommand command, CancellationToken ct)
    {
        var user = await _users.GetById(command.UserId);

        if (user is null)
        {
            _log.LogWarning("User not found for profile update: {UserId}", command.UserId);
            throw new InvalidOperationException("User not found");
        }

        // Update only provided fields
        if (command.FullName is not null) user.FullName = command.FullName;
        if (command.JobTitle is not null) user.JobTitle = command.JobTitle;
        if (command.AvatarUrl is not null) user.AvatarUrl = command.AvatarUrl;
        if (command.PhoneNumber is not null) user.PhoneNumber = command.PhoneNumber;
        if (command.Bio is not null) user.Bio = command.Bio;
        if (command.PreferredLanguage is not null) user.PreferredLanguage = command.PreferredLanguage;
        if (command.Timezone is not null) user.Timezone = command.Timezone;

        await _users.Update(user);

        _log.LogInformation("Profile updated for user {Username}", user.Username);

        return new UserProfileResponse(
            user.Id,
            user.Username,
            user.Email,
            user.FullName,
            user.JobTitle,
            user.AvatarUrl,
            user.PhoneNumber,
            user.Bio,
            user.PreferredLanguage ?? "en",
            user.Timezone ?? "UTC",
            user.GetRoles().Select(r => r.ToString()).ToList()
        );
    }
}
