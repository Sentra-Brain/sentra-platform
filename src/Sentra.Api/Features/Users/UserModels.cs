using Sentra.Domain.Enums;
using System.Linq.Expressions;

namespace Sentra.Api.Features.Users;

/// <summary>
/// User model for API responses.
/// </summary>
public sealed record UserResponse(
    Guid Id,
    string Username,
    string Email,
    string? FullName,
    bool Disabled,
    List<string> Roles
)
{
    /// <summary>
    /// Expression to project from User entity to UserResponse.
    /// </summary>
    public static Expression<Func<Domain.Entities.User, UserResponse>> Projection =>
        u => new UserResponse(
            u.Id,
            u.Username,
            u.Email,
            u.FullName,
            u.Disabled,
            u.Roles.Split(',', StringSplitOptions.RemoveEmptyEntries).ToList()
        );
}

/// <summary>
/// Request model for user signup.
/// </summary>
public sealed record SignupRequest(
    string Username,
    string Email,
    string FullName,
    string Password
);

/// <summary>
/// Response model for signup operation.
/// </summary>
public sealed record SignupResponse(
    UserResponse User,
    string Message
);

/// <summary>
/// Request model for updating user profile.
/// </summary>
public sealed record UpdateProfileRequest(
    string? FullName = null,
    string? JobTitle = null,
    string? AvatarUrl = null,
    string? PhoneNumber = null,
    string? Bio = null,
    string? PreferredLanguage = null,
    string? Timezone = null
);

/// <summary>
/// Request model for updating another user (admin operation).
/// </summary>
public sealed record UpdateUserRequest(
    string? Password = null
);

/// <summary>
/// Extended user profile response with additional fields.
/// </summary>
public sealed record UserProfileResponse(
    Guid Id,
    string Username,
    string Email,
    string? FullName,
    string? JobTitle,
    string? AvatarUrl,
    string? PhoneNumber,
    string? Bio,
    string PreferredLanguage,
    string Timezone,
    List<string> Roles
)
{
    /// <summary>
    /// Expression to project from User entity to UserProfileResponse.
    /// </summary>
    public static Expression<Func<Domain.Entities.User, UserProfileResponse>> Projection =>
        u => new UserProfileResponse(
            u.Id,
            u.Username,
            u.Email,
            u.FullName,
            u.JobTitle,
            u.AvatarUrl,
            u.PhoneNumber,
            u.Bio,
            u.PreferredLanguage,
            u.Timezone,
            u.Roles.Split(',', StringSplitOptions.RemoveEmptyEntries).ToList()
        );
}
