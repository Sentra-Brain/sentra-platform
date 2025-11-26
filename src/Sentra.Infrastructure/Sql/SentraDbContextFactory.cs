using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;

namespace Sentra.Infrastructure.Sql;

public sealed class SentraDbContextFactory : IDesignTimeDbContextFactory<SentraDbContext>
{
    public SentraDbContext CreateDbContext(string[] args)
    {
        // Design-time only. Does not affect runtime.
        var cs = "Host=localhost;Port=5432;Database=sentra-brain-sql;Username=postgres;Password=postgres";

        var options = new DbContextOptionsBuilder<SentraDbContext>()
            .UseNpgsql(cs, npg => npg.MigrationsAssembly("Sentra.Infrastructure"))
            .Options;

        return new SentraDbContext(options);
    }
}
