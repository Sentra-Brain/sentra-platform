using Microsoft.EntityFrameworkCore;
using Sentra.Application.Users;
using Sentra.Domain.Entities;

namespace Sentra.Infrastructure.Sql.Repositories;

public sealed class UserRepository : IUserRepository
{
    private readonly SentraDbContext _db;

    public UserRepository(SentraDbContext db) => _db = db;

    public Task<UserEntity?> GetById(Guid id) =>
        _db.Users.FirstOrDefaultAsync(u => u.Id == id);

    public Task<UserEntity?> GetByUsername(string username) =>
        _db.Users.FirstOrDefaultAsync(u => u.Username == username);

    public Task<UserEntity?> GetByEmail(string email) =>
        _db.Users.FirstOrDefaultAsync(u => u.Email == email);

    public async Task Add(UserEntity user)
    {
        await _db.Users.AddAsync(user);
        await _db.SaveChangesAsync();
    }

    public async Task Update(UserEntity user)
    {
        _db.Users.Update(user);
        await _db.SaveChangesAsync();
    }
}
