using Microsoft.EntityFrameworkCore;
using Sentra.Domain.Entities;
using Sentra.Domain.Enums;

namespace Sentra.Infrastructure.Sql;

public class SentraDbContext : DbContext
{
    public DbSet<User> Users => Set<User>();
    public DbSet<Document> Documents => Set<Document>();
    public DbSet<Conversation> Conversations => Set<Conversation>();
    public DbSet<KnowledgeSource> KnowledgeSources => Set<KnowledgeSource>();
    public DbSet<Organization> Organizations => Set<Organization>();
    public DbSet<SystemSettings> SystemSettings => Set<SystemSettings>();
    public DbSet<ChatSettings> ChatSettings => Set<ChatSettings>();

    public SentraDbContext(DbContextOptions<SentraDbContext> options)
        : base(options) { }

    protected override void OnModelCreating(ModelBuilder b)
    {
        b.ApplyUtcDateTimeConverters();
        ConfigureEnums(b);
        ConfigureRelationships(b);
    }

    static void ConfigureEnums(ModelBuilder b)
    {
        b.Entity<Document>()
            .Property(x => x.Filetype)
            .HasConversion<string>();

        b.Entity<Document>()
            .Property(x => x.Status)
            .HasConversion<string>();

        b.Entity<KnowledgeSource>()
            .Property(x => x.Type)
            .HasConversion<string>();

        b.Entity<KnowledgeSource>()
            .Property(x => x.Visibility)
            .HasConversion<string>();

        b.Entity<KnowledgeSource>()
            .Property(x => x.Status)
            .HasConversion<string>();
    }

    static void ConfigureRelationships(ModelBuilder b)
    {
        b.Entity<User>()
            .HasMany(u => u.Conversations)
            .WithOne(c => c.CreatedBy)
            .HasForeignKey(c => c.CreatedById)
            .OnDelete(DeleteBehavior.Restrict);

        b.Entity<User>()
            .HasMany(u => u.Documents)
            .WithOne(d => d.CreatedBy)
            .HasForeignKey(d => d.CreatedById)
            .OnDelete(DeleteBehavior.Restrict);

        b.Entity<User>()
            .HasMany(u => u.KnowledgeSources)
            .WithOne(k => k.CreatedBy)
            .HasForeignKey(k => k.CreatedById)
            .OnDelete(DeleteBehavior.Restrict);

        b.Entity<Document>()
            .HasOne(d => d.KnowledgeSource)
            .WithMany()
            .HasForeignKey(d => d.KnowledgeSourceId)
            .OnDelete(DeleteBehavior.Cascade);
    }
}
