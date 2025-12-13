using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Kommand;
using Sentra.Api.Features.Conversations.Commands;

namespace Sentra.Api.Features.Conversations.Validators;

public sealed class UpdateConversationCommandValidator : IValidator<UpdateConversationCommand>
{
    public Task<ValidationResult> ValidateAsync(UpdateConversationCommand command, CancellationToken ct)
    {
        var errors = new List<ValidationError>();

        if (command.ConversationId == Guid.Empty)
        {
            errors.Add(new ValidationError(nameof(command.ConversationId), "ConversationId is required"));
        }

        if (command.UserId == Guid.Empty)
        {
            errors.Add(new ValidationError(nameof(command.UserId), "UserId is required"));
        }

        // At least one field must be provided
        if (string.IsNullOrWhiteSpace(command.Title) && string.IsNullOrWhiteSpace(command.Description))
        {
            errors.Add(new ValidationError(nameof(command.Title), "At least one of Title or Description must be provided"));
        }

        if (!string.IsNullOrWhiteSpace(command.Title) && command.Title.Length > 200)
        {
            errors.Add(new ValidationError(nameof(command.Title), "Title must not exceed 200 characters"));
        }

        if (!string.IsNullOrWhiteSpace(command.Description) && command.Description.Length > 1000)
        {
            errors.Add(new ValidationError(nameof(command.Description), "Description must not exceed 1000 characters"));
        }

        return Task.FromResult(errors.Count > 0
            ? ValidationResult.Failure(errors.ToArray())
            : ValidationResult.Success());
    }
}
