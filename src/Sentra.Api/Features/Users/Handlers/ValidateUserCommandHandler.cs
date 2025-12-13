using Kommand.Abstractions;
using Sentra.Api.Features.Users.Commands;
using Sentra.Application.Users;
using Sentra.Contracts.Users;

namespace Sentra.Api.Features.Users.Handlers;

/// <summary>
/// Handles user account validation via email verification token.
/// Note: This is a simplified version. Full implementation would need JWT token validation.
/// </summary>
public sealed class ValidateUserCommandHandler : ICommandHandler<ValidateUserCommand, UserResponse>
{
    private readonly IUserRepository _users;
    private readonly ILogger<ValidateUserCommandHandler> _log;

    public ValidateUserCommandHandler(
        IUserRepository users,
        ILogger<ValidateUserCommandHandler> log)
    {
        _users = users;
        _log = log;
    }

    public async Task<UserResponse> HandleAsync(ValidateUserCommand command, CancellationToken ct)
    {
        // TODO: Implement token validation logic
        // This should decode a JWT token containing user ID and enable the user
        
        _log.LogWarning("ValidateUserCommand not fully implemented - token: {Token}", command.Token);
        throw new NotImplementedException("Email verification not yet implemented");

        // Example implementation:
        // var userId = DecodeVerificationToken(command.Token);
        // var user = await _users.GetById(userId);
        // user.Disabled = false;
        // await _users.Update(user);
        // await _users.SaveChangesAsync(ct);
        // return new UserResponse(...);
    }
}
