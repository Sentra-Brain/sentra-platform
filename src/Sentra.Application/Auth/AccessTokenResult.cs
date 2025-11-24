namespace Sentra.Application.Auth;

public record AccessTokenResult(string AccessToken, string TokenType = "bearer");

