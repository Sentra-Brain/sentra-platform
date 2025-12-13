using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Kommand;
using Sentra.Api.Features.Conversations.Commands;

namespace Sentra.Api.Features.Conversations.Validators;

public sealed class CreateConversationCommandValidator : IValidator<CreateConversationCommand>
{
    public Task<ValidationResult> ValidateAsync(CreateConversationCommand command, CancellationToken ct)
    {
        var errors = new List<ValidationError>();

        if (command.UserId == Guid.Empty)
        {
            errors.Add(new ValidationError(nameof(command.UserId), "UserId is required"));
        }

        if (string.IsNullOrWhiteSpace(command.InitialPrompt))
        {
            errors.Add(new ValidationError(nameof(command.InitialPrompt), "InitialPrompt is required"));
        }
        else if (command.InitialPrompt.Length < 1)
        {
            errors.Add(new ValidationError(nameof(command.InitialPrompt), "InitialPrompt must be at least 1 character"));
        }
        else if (command.InitialPrompt.Length > 10000)
        {
            errors.Add(new ValidationError(nameof(command.InitialPrompt), "InitialPrompt must not exceed 10000 characters"));
        }

        return Task.FromResult(errors.Count > 0
            ? ValidationResult.Failure(errors.ToArray())
            : ValidationResult.Success());
    }
}
