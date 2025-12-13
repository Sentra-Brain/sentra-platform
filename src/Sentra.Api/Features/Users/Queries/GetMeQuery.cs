using Kommand.Abstractions;
using Sentra.Api.Features.Users;

namespace Sentra.Api.Features.Users.Queries;

/// <summary>
/// Query to get the current authenticated user's information.
/// </summary>
public sealed record GetMeQuery(
    Guid UserId
) : IQuery<UserResponse>;
