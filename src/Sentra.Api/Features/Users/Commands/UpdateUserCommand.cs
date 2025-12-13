using Kommand.Abstractions;
using Sentra.Contracts.Users;

namespace Sentra.Api.Features.Users.Commands;

/// <summary>
/// Command to update another user (admin operation).
/// </summary>
public sealed record UpdateUserCommand(
    Guid CurrentUserId,
    Guid UserToUpdateId,
    string? Password
) : ICommand<UserResponse>;
