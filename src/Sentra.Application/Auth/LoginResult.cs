namespace Sentra.Application.Auth
{
    public record LoginResult(string AccessToken, string RefreshToken, string TokenType = "bearer");

}
