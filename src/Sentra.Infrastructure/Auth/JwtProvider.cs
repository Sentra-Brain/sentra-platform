using Microsoft.Extensions.Options;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Sentra.Application.Auth;

namespace Sentra.Infrastructure.Auth;
public sealed class JwtProvider : IJwtProvider
{
    private readonly JwtOptions _opts;

    public JwtProvider(IOptions<JwtOptions> opts) => _opts = opts.Value;

    public string CreateAccessToken(string username, string roles, TimeSpan expires) =>
        Create(username, roles, expires, false);

    public string CreateRefreshToken(string username, string roles, TimeSpan expires) =>
        Create(username, roles, expires, true);

    public (string? Username, string? Roles, bool IsRefreshToken) ValidateToken(string token)
    {
        var handler = new JwtSecurityTokenHandler();

        try
        {
            var principal = handler.ValidateToken(
                token,
                _opts.ValidationParameters,
                out _
            );

            string? username = principal.Claims.FirstOrDefault(c => c.Type == "sub")?.Value;
            string? roles = principal.Claims.FirstOrDefault(c => c.Type == "roles")?.Value;
            bool isRefresh = principal.Claims.FirstOrDefault(c => c.Type == "typ")?.Value == "refresh";

            return (username, roles, isRefresh);
        }
        catch
        {
            return (null, null, false);
        }
    }

    private string Create(string username, string roles, TimeSpan expires, bool isRefresh)
    {
        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_opts.Secret));
        var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

        var claims = new[]
        {
            new Claim("sub", username),
            new Claim("roles", roles),
            new Claim("typ", isRefresh ? "refresh" : "access")
        };

        var token = new JwtSecurityToken(
            issuer: _opts.Issuer,
            audience: _opts.Audience,
            claims: claims,
            expires: DateTime.UtcNow.Add(expires),
            signingCredentials: creds
        );

        return new JwtSecurityTokenHandler().WriteToken(token);
    }
}