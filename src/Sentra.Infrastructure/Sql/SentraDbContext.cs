using Microsoft.EntityFrameworkCore;
using Sentra.Domain.Entities;
using Sentra.Domain.Enums;

namespace Sentra.Infrastructure.Sql;

public class SentraDbContext : DbContext
{
    public DbSet<UserEntity> Users => Set<UserEntity>();
    public DbSet<DocumentEntity> Documents => Set<DocumentEntity>();
    public DbSet<ConversationEntity> Conversations => Set<ConversationEntity>();
    public DbSet<KnowledgeSourceEntity> KnowledgeSources => Set<KnowledgeSourceEntity>();
    public DbSet<OrganizationEntity> Organizations => Set<OrganizationEntity>();
    public DbSet<SystemSettingsEntity> SystemSettings => Set<SystemSettingsEntity>();
    public DbSet<ChatSettingsEntity> ChatSettings => Set<ChatSettingsEntity>();

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
        b.Entity<DocumentEntity>()
            .Property(x => x.Filetype)
            .HasConversion<string>();

        b.Entity<DocumentEntity>()
            .Property(x => x.Status)
            .HasConversion<string>();

        b.Entity<KnowledgeSourceEntity>()
            .Property(x => x.Type)
            .HasConversion<string>();

        b.Entity<KnowledgeSourceEntity>()
            .Property(x => x.Visibility)
            .HasConversion<string>();

        b.Entity<KnowledgeSourceEntity>()
            .Property(x => x.Status)
            .HasConversion<string>();
    }

    static void ConfigureRelationships(ModelBuilder b)
    {
        b.Entity<UserEntity>()
            .HasMany(u => u.Conversations)
            .WithOne(c => c.CreatedBy)
            .HasForeignKey(c => c.CreatedById)
            .OnDelete(DeleteBehavior.Restrict);

        b.Entity<UserEntity>()
            .HasMany(u => u.Documents)
            .WithOne(d => d.CreatedBy)
            .HasForeignKey(d => d.CreatedById)
            .OnDelete(DeleteBehavior.Restrict);

        b.Entity<UserEntity>()
            .HasMany(u => u.KnowledgeSources)
            .WithOne(k => k.CreatedBy)
            .HasForeignKey(k => k.CreatedById)
            .OnDelete(DeleteBehavior.Restrict);

        b.Entity<DocumentEntity>()
            .HasOne(d => d.KnowledgeSource)
            .WithMany()
            .HasForeignKey(d => d.KnowledgeSourceId)
            .OnDelete(DeleteBehavior.Cascade);
    }
}
