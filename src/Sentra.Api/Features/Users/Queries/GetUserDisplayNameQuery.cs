using Kommand.Abstractions;

namespace Sentra.Api.Features.Users.Queries;

/// <summary>
/// Query to get a user's display name by their ID.
/// </summary>
public sealed record GetUserDisplayNameQuery(
    Guid UserId
) : IQuery<string>;
