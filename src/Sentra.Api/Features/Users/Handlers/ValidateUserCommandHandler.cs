using Kommand.Abstractions;
using Microsoft.EntityFrameworkCore;
using Sentra.Api.Features.Users.Commands;
using Sentra.Infrastructure.Sql;

namespace Sentra.Api.Features.Users.Handlers;

/// <summary>
/// Handles user account validation via email verification token.
/// Note: This is a simplified version. Full implementation would need JWT token validation.
/// </summary>
public sealed class ValidateUserCommandHandler : ICommandHandler<ValidateUserCommand, UserResponse>
{
    private readonly SentraDbContext _db;
    private readonly ILogger<ValidateUserCommandHandler> _log;

    public ValidateUserCommandHandler(
        SentraDbContext db,
        ILogger<ValidateUserCommandHandler> log)
    {
        _db = db;
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
        // var user = await _db.Users.FindAsync(userId, ct);
        // user.Disabled = false;
        // await _db.SaveChangesAsync(ct);
        // return await _db.Users.Where(u => u.Id == userId).Select(UserResponse.Projection).FirstAsync(ct);
    }
}
