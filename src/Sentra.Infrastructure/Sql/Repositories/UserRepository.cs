using Microsoft.EntityFrameworkCore;
using Sentra.Application.Users;
using Sentra.Domain.Entities;

namespace Sentra.Infrastructure.Sql.Repositories;

public sealed class UserRepository : IUserRepository
{
    private readonly SentraDbContext _db;

    public UserRepository(SentraDbContext db) => _db = db;

    public Task<User?> GetById(Guid id) =>
        _db.Users.FirstOrDefaultAsync(u => u.Id == id);

    public Task<User?> GetByUsername(string username) =>
        _db.Users.FirstOrDefaultAsync(u => u.Username == username);

    public Task<User?> GetByEmail(string email) =>
        _db.Users.FirstOrDefaultAsync(u => u.Email == email);

    public async Task Add(User user)
    {
        await _db.Users.AddAsync(user);
        await _db.SaveChangesAsync();
    }

    public async Task Update(User user)
    {
        _db.Users.Update(user);
        await _db.SaveChangesAsync();
    }
}
