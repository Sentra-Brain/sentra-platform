using Sentra.Application.Security;

public sealed class PasswordHasher : IPasswordHasher
{
    public string Hash(string value) =>
        BCrypt.Net.BCrypt.HashPassword(value);

    public bool Verify(string plain, string hashed) =>
        BCrypt.Net.BCrypt.Verify(plain, hashed);
}
