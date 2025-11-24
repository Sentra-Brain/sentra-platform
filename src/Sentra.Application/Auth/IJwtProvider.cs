namespace Sentra.Application.Auth;

public interface IJwtProvider
{
    string CreateAccessToken(string username, string roles, TimeSpan expires);
    string CreateRefreshToken(string username, string roles, TimeSpan expires);
    (string? Username, string? Roles, bool IsRefreshToken) ValidateToken(string token);
}
