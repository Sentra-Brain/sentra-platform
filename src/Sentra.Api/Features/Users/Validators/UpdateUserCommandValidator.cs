using Kommand;
using Sentra.Api.Features.Users.Commands;

namespace Sentra.Api.Features.Users.Validators;

/// <summary>
/// Validates update user command inputs.
/// </summary>
public sealed class UpdateUserCommandValidator : IValidator<UpdateUserCommand>
{
    public Task<ValidationResult> ValidateAsync(UpdateUserCommand command, CancellationToken ct)
    {
        var errors = new List<ValidationError>();

        // Validate password if provided
        if (command.Password is not null && command.Password.Length < 8)
        {
            errors.Add(new ValidationError(nameof(command.Password), "Password must be at least 8 characters"));
        }

        return Task.FromResult(
            errors.Count > 0
                ? ValidationResult.Failure(errors)
                : ValidationResult.Success()
        );
    }
}
