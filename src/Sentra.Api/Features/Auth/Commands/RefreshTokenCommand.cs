using Kommand.Abstractions;
using Sentra.Api.Features.Auth;

namespace Sentra.Api.Features.Auth.Commands;

/// <summary>
/// Command to refresh an access token using a refresh token.
/// </summary>
public sealed record RefreshTokenCommand(
    string RefreshToken
) : ICommand<RefreshTokenResponse>;
