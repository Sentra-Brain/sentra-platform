using Kommand.Abstractions;
using Microsoft.EntityFrameworkCore;
using Sentra.Api.Features.Conversations.Commands;
using Sentra.Domain.Entities;
using Sentra.Infrastructure.Sql;

namespace Sentra.Api.Features.Conversations.Handlers;

public sealed class CreateConversationCommandHandler : ICommandHandler<CreateConversationCommand, CreateConversationResponse>
{
    private readonly SentraDbContext _db;

    public CreateConversationCommandHandler(SentraDbContext db)
    {
        _db = db;
    }

    public async Task<CreateConversationResponse> HandleAsync(CreateConversationCommand command, CancellationToken cancellationToken)
    {
        var conversation = new Conversation
        {
            Id = Guid.NewGuid(),
            Title = "Untitled",
            InitialPrompt = command.InitialPrompt,
            CreatedById = command.UserId,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        _db.Conversations.Add(conversation);
        await _db.SaveChangesAsync(cancellationToken);

        // TODO: Schedule background title generation using initial prompt
        // This would call an agent service to generate a proper title asynchronously

        return new CreateConversationResponse(
            conversation.Id,
            conversation.Title ?? "Untitled",
            conversation.CreatedAt
        );
    }
}
