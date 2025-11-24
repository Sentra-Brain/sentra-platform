using Sentra.Domain.Entities;

namespace Sentra.Application.Users;

public interface IUserRepository
{
    Task<UserEntity?> GetByUsername(string username);
    Task<UserEntity?> GetByEmail(string email);
    Task<UserEntity?> GetById(Guid id);

    Task Add(UserEntity user);
    Task Update(UserEntity user);
}
