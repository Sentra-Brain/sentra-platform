using Kommand.Abstractions;
using Kommand;
using Sentra.Api.Features.Auth.Commands;

namespace Sentra.Api.Features.Auth.Validators;

/// <summary>
/// Validates login command inputs.
/// </summary>
public sealed class LoginCommandValidator : IValidator<LoginCommand>
{
    public Task<ValidationResult> ValidateAsync(LoginCommand request, CancellationToken ct)
    {
        var errors = new List<ValidationError>();

        if (string.IsNullOrWhiteSpace(request.EmailOrUsername))
        {
            errors.Add(new ValidationError(
                nameof(request.EmailOrUsername),
                "Email or username is required"
            ));
        }

        if (string.IsNullOrWhiteSpace(request.Password))
        {
            errors.Add(new ValidationError(
                nameof(request.Password),
                "Password is required"
            ));
        }

        return Task.FromResult(
            errors.Count > 0
                ? ValidationResult.Failure(errors)
                : ValidationResult.Success()
        );
    }
}
