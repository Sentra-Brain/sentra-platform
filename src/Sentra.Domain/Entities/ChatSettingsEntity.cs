using System.ComponentModel.DataAnnotations.Schema;

namespace Sentra.Domain.Entities;

[Table("chat_settings")]
public class ChatSettingsEntity : BaseEntity
{
    public int MaxTokens { get; set; } = 2048;
    public float Temperature { get; set; } = 0.7f;
    public float TopP { get; set; } = 0.9f;
    public int TopK { get; set; } = 40;
    public string SystemPrompt { get; set; } = "Responde siempre en español.";
    public string StopSequences { get; set; } = ",User:,Assistant:";
}
