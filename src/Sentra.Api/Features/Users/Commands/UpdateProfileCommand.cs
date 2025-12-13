using Kommand.Abstractions;
using Sentra.Api.Features.Users;

namespace Sentra.Api.Features.Users.Commands;

/// <summary>
/// Command to update the current user's profile fields.
/// </summary>
public sealed record UpdateProfileCommand(
    Guid UserId,
    string? FullName,
    string? JobTitle,
    string? AvatarUrl,
    string? PhoneNumber,
    string? Bio,
    string? PreferredLanguage,
    string? Timezone
) : ICommand<UserProfileResponse>;
