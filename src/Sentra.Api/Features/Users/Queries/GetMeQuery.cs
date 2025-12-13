using Kommand.Abstractions;
using Sentra.Contracts.Users;

namespace Sentra.Api.Features.Users.Queries;

/// <summary>
/// Query to get the current authenticated user's information.
/// </summary>
public sealed record GetMeQuery(
    Guid UserId
) : IQuery<UserResponse>;
