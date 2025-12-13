using Kommand.Abstractions;
using Kommand;
using Sentra.Api.Features.Auth.Commands;

namespace Sentra.Api.Features.Auth.Validators;

/// <summary>
/// Validates refresh token command inputs.
/// </summary>
public sealed class RefreshTokenCommandValidator : IValidator<RefreshTokenCommand>
{
    public Task<ValidationResult> ValidateAsync(RefreshTokenCommand request, CancellationToken ct)
    {
        var errors = new List<ValidationError>();

        if (string.IsNullOrWhiteSpace(request.RefreshToken))
        {
            errors.Add(new ValidationError(
                nameof(request.RefreshToken),
                "Refresh token is required"
            ));
        }

        return Task.FromResult(
            errors.Count > 0
                ? ValidationResult.Failure(errors)
                : ValidationResult.Success()
        );
    }
}
