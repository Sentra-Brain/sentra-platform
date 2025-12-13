using Kommand.Abstractions;
using Microsoft.EntityFrameworkCore;
using Sentra.Api.Features.Conversations.Commands;
using Sentra.Infrastructure.Sql;

namespace Sentra.Api.Features.Conversations.Handlers;

public sealed class DeleteConversationCommandHandler : ICommandHandler<DeleteConversationCommand, DeleteConversationResponse>
{
    private readonly SentraDbContext _db;

    public DeleteConversationCommandHandler(SentraDbContext db)
    {
        _db = db;
    }

    public async Task<DeleteConversationResponse> HandleAsync(DeleteConversationCommand command, CancellationToken cancellationToken)
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

        // Soft delete
        conversation.DeletedAt = DateTime.UtcNow;
        await _db.SaveChangesAsync(cancellationToken);

        return new DeleteConversationResponse(
            true,
            "Conversation deleted successfully"
        );
    }
}
