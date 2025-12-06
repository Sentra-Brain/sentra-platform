using Sentra.Domain.Entities;

namespace Sentra.Application.Users;

public interface IUserRepository
{
    Task<User?> GetByUsername(string username);
    Task<User?> GetByEmail(string email);
    Task<User?> GetById(Guid id);

    Task Add(User user);
    Task Update(User user);
}
