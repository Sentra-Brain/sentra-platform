using Kommand.Abstractions;
using Sentra.Contracts.Users;

namespace Sentra.Api.Features.Users.Commands;

/// <summary>
/// Command to register a new user account.
/// </summary>
public sealed record SignupCommand(
    string Username,
    string Email,
    string FullName,
    string Password
) : ICommand<SignupResponse>;
