using Kommand.Abstractions;
using Sentra.Contracts.Users;

namespace Sentra.Api.Features.Users.Commands;

/// <summary>
/// Command to validate a user account using email verification token.
/// </summary>
public sealed record ValidateUserCommand(
    string Token
) : ICommand<UserResponse>;
