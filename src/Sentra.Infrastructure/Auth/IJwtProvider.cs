namespace Sentra.Application.Auth;

/// <summary>
/// Service for creating and validating JWT tokens.
/// </summary>
public interface IJwtProvider
{
    /// <summary>
    /// Creates a new access token.
    /// </summary>
    string CreateAccessToken(string username, string roles, TimeSpan expires);
    
    /// <summary>
    /// Creates a new refresh token.
    /// </summary>
    string CreateRefreshToken(string username, string roles, TimeSpan expires);
    
    /// <summary>
    /// Validates a token and extracts claims.
    /// </summary>
    (string? Username, string? Roles, bool IsRefreshToken) ValidateToken(string token);
}
