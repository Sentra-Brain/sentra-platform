using Kommand.Abstractions;
using Sentra.Api.Features.Auth;

namespace Sentra.Api.Features.Auth.Commands;

/// <summary>
/// Command to authenticate a user and generate access/refresh tokens.
/// </summary>
public sealed record LoginCommand(
    string EmailOrUsername,
    string Password
) : ICommand<LoginResponse>;
