namespace Sentra.Api.Features.Auth;

/// <summary>
/// Response model for login operation.
/// </summary>
public sealed record LoginResponse(
    string AccessToken,
    string RefreshToken,
    string TokenType = "Bearer"
);

/// <summary>
/// Response model for token refresh operation.
/// </summary>
public sealed record RefreshTokenResponse(
    string AccessToken,
    string TokenType = "Bearer"
);

/// <summary>
/// Request model for login endpoint.
/// </summary>
public sealed record LoginRequest(
    string EmailOrUsername,
    string Password
);

/// <summary>
/// Request model for refresh token endpoint.
/// </summary>
public sealed record RefreshRequest(
    string RefreshToken
);
