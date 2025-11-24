namespace Sentra.Application.Security;

public interface IPasswordHasher
{
    string Hash(string value);
    bool Verify(string plain, string hashed);
}
