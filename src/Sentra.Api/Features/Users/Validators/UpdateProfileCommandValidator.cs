using Kommand;
using Sentra.Api.Features.Users.Commands;

namespace Sentra.Api.Features.Users.Validators;

/// <summary>
/// Validates update profile command inputs.
/// </summary>
public sealed class UpdateProfileCommandValidator : IValidator<UpdateProfileCommand>
{
    public Task<ValidationResult> ValidateAsync(UpdateProfileCommand command, CancellationToken ct)
    {
        var errors = new List<ValidationError>();

        // At least one field should be provided
        if (command.FullName is null &&
            command.JobTitle is null &&
            command.AvatarUrl is null &&
            command.PhoneNumber is null &&
            command.Bio is null &&
            command.PreferredLanguage is null &&
            command.Timezone is null)
        {
            errors.Add(new ValidationError("Profile", "At least one field must be provided for update"));
        }

        // Validate full name if provided
        if (command.FullName is not null && command.FullName.Length < 2)
        {
            errors.Add(new ValidationError(nameof(command.FullName), "Full name must be at least 2 characters"));
        }

        // Validate avatar URL if provided
        if (command.AvatarUrl is not null && !string.IsNullOrWhiteSpace(command.AvatarUrl))
        {
            if (!Uri.TryCreate(command.AvatarUrl, UriKind.Absolute, out var uri) ||
                (uri.Scheme != Uri.UriSchemeHttp && uri.Scheme != Uri.UriSchemeHttps))
            {
                errors.Add(new ValidationError(nameof(command.AvatarUrl), "Avatar URL must be a valid HTTP/HTTPS URL"));
            }
        }

        return Task.FromResult(
            errors.Count > 0
                ? ValidationResult.Failure(errors)
                : ValidationResult.Success()
        );
    }
}
