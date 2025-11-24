namespace Sentra.Application.Auth
{
    public interface IAuthService
    {
        Task<LoginResult> Login(string username, string password);
        Task<AccessTokenResult> Refresh(string refreshToken);
    }

}
