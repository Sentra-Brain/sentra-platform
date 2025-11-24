using Microsoft.EntityFrameworkCore;
using Sentra.Domain.Entities;
using System.Collections.Generic;

namespace Sentra.Infrastructure.Sql;

public class SentraDbContext : DbContext
{
    public DbSet<UserEntity> Users => Set<UserEntity>();

    public SentraDbContext(DbContextOptions<SentraDbContext> opts)
        : base(opts) { }
}
