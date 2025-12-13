using Kommand.Abstractions;
using Microsoft.EntityFrameworkCore;
using Sentra.Api.Features.Conversations.Commands;
using Sentra.Infrastructure.Sql;

namespace Sentra.Api.Features.Conversations.Handlers;

public sealed class GenerateTitleCommandHandler : ICommandHandler<GenerateTitleCommand, GenerateTitleResponse>
{
    private readonly SentraDbContext _db;

    public GenerateTitleCommandHandler(SentraDbContext db)
    {
        _db = db;
    }

    public async Task<GenerateTitleResponse> HandleAsync(GenerateTitleCommand command, CancellationToken cancellationToken)
    {
        var conversation = await _db.Conversations
            .Where(c => c.DeletedAt == null)
            .Where(c => c.Id == command.ConversationId)
            .Where(c => c.CreatedById == command.UserId)
            .FirstOrDefaultAsync(cancellationToken);

        if (conversation == null)
        {
            throw new InvalidOperationException("Conversation not found");
        }

        // TODO: Implement title generation using TitleAgent
        // For now, use a placeholder title based on timestamp
        var generatedTitle = $"Conversation {DateTime.UtcNow:yyyy-MM-dd HH:mm}";

        conversation.Title = generatedTitle;
        conversation.UpdatedAt = DateTime.UtcNow;

        await _db.SaveChangesAsync(cancellationToken);

        return new GenerateTitleResponse(
            conversation.Id,
            conversation.Title
        );
    }
}
