using Kommand.Abstractions;
using Microsoft.EntityFrameworkCore;
using Sentra.Api.Features.Conversations.Commands;
using Sentra.Infrastructure.Sql;

namespace Sentra.Api.Features.Conversations.Handlers;

public sealed class UpdateConversationCommandHandler : ICommandHandler<UpdateConversationCommand, UpdateConversationResponse>
{
    private readonly SentraDbContext _db;

    public UpdateConversationCommandHandler(SentraDbContext db)
    {
        _db = db;
    }

    public async Task<UpdateConversationResponse> HandleAsync(UpdateConversationCommand command, CancellationToken cancellationToken)
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

        // Update fields if provided
        if (!string.IsNullOrWhiteSpace(command.Title))
        {
            conversation.Title = command.Title;
        }

        if (!string.IsNullOrWhiteSpace(command.Description))
        {
            conversation.Description = command.Description;
        }

        conversation.UpdatedAt = DateTime.UtcNow;

        await _db.SaveChangesAsync(cancellationToken);

        return new UpdateConversationResponse(
            conversation.Id,
            conversation.Title,
            conversation.Description
        );
    }
}
