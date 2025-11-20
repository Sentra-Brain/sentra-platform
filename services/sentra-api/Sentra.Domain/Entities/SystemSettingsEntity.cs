using System.ComponentModel.DataAnnotations.Schema;

namespace Sentra.Domain.Entities;

[Table("system_settings")]
public class SystemSettingsEntity : BaseEntity
{
    public string WorkspaceName { get; set; } = "Sentra Brain";
    public string LicenseType { get; set; } = "community";
    public bool MaintenanceMode { get; set; } = false;
    public string DefaultLanguage { get; set; } = "en";
    public int LogRetentionDays { get; set; } = 30;
    public int MaxUsers { get; set; } = 3;

    public bool EnableWebSearch { get; set; } = true;
    public string WebSearchRegion { get; set; } = "España";
    public int MaxWebResults { get; set; } = 5;
    public bool CacheResults { get; set; } = false;
    public int CacheExpirationHours { get; set; } = 6;
    public int ContextLimitChars { get; set; } = 1500;
    public string DefaultTimezone { get; set; } = "Europe/Madrid";
}
