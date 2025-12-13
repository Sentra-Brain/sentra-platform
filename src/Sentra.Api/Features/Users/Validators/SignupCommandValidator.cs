using Kommand;
using Sentra.Api.Features.Users.Commands;
using System.Text.RegularExpressions;

namespace Sentra.Api.Features.Users.Validators;

/// <summary>
/// Validates signup command inputs.
/// </summary>
public sealed partial class SignupCommandValidator : IValidator<SignupCommand>
{
    [GeneratedRegex(@"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")]
    private static partial Regex EmailRegex();

    public Task<ValidationResult> ValidateAsync(SignupCommand command, CancellationToken ct)
    {
        var errors = new List<ValidationError>();

        // Username validation
        if (string.IsNullOrWhiteSpace(command.Username))
        {
            errors.Add(new ValidationError(nameof(command.Username), "Username is required"));
        }
        else if (command.Username.Length < 3)
        {
            errors.Add(new ValidationError(nameof(command.Username), "Username must be at least 3 characters"));
        }
        else if (command.Username.Length > 50)
        {
            errors.Add(new ValidationError(nameof(command.Username), "Username must not exceed 50 characters"));
        }

        // Email validation
        if (string.IsNullOrWhiteSpace(command.Email))
        {
            errors.Add(new ValidationError(nameof(command.Email), "Email is required"));
        }
        else if (!EmailRegex().IsMatch(command.Email))
        {
            errors.Add(new ValidationError(nameof(command.Email), "Email format is invalid"));
        }

        // Full name validation
        if (string.IsNullOrWhiteSpace(command.FullName))
        {
            errors.Add(new ValidationError(nameof(command.FullName), "Full name is required"));
        }
        else if (command.FullName.Length < 2)
        {
            errors.Add(new ValidationError(nameof(command.FullName), "Full name must be at least 2 characters"));
        }

        // Password validation
        if (string.IsNullOrWhiteSpace(command.Password))
        {
            errors.Add(new ValidationError(nameof(command.Password), "Password is required"));
        }
        else if (command.Password.Length < 8)
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
