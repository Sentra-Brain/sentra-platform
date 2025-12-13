using Kommand.Abstractions;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Sentra.Api.Features.Users.Commands;
using Sentra.Api.Features.Users.Queries;
using Sentra.Contracts.Users;
using System.Security.Claims;

namespace Sentra.Api.Features.Users;

/// <summary>
/// User management endpoints for signup, profile, and user operations.
/// </summary>
public static class UserEndpoints
{
    public static RouteGroupBuilder MapUserEndpoints(this WebApplication app)
    {
        var group = app.MapGroup("/users")
            .WithTags("Users");

        // Public endpoint - signup
        group.MapPost("/signup", Signup)
            .WithName("Signup")
            .WithSummary("Register a new user account")
            .Produces<SignupResponse>(StatusCodes.Status200OK)
            .Produces<ProblemDetails>(StatusCodes.Status400BadRequest)
            .AllowAnonymous();

        // Authenticated endpoints
        group.MapGet("/me", GetMe)
            .WithName("GetMe")
            .WithSummary("Get current authenticated user information")
            .Produces<UserResponse>(StatusCodes.Status200OK)
            .RequireAuthorization();

        group.MapPatch("/me", UpdateProfile)
            .WithName("UpdateProfile")
            .WithSummary("Update current user's profile")
            .Produces<UserProfileResponse>(StatusCodes.Status200OK)
            .Produces<ProblemDetails>(StatusCodes.Status400BadRequest)
            .RequireAuthorization();

        group.MapPut("/{userToUpdateId:guid}", UpdateUser)
            .WithName("UpdateUser")
            .WithSummary("Update another user (admin operation)")
            .Produces<UserResponse>(StatusCodes.Status200OK)
            .Produces<ProblemDetails>(StatusCodes.Status404NotFound)
            .RequireAuthorization(); // TODO: Add admin role requirement

        group.MapGet("/validate", ValidateUser)
            .WithName("ValidateUser")
            .WithSummary("Validate user account via email verification token")
            .Produces<UserResponse>(StatusCodes.Status200OK)
            .Produces<ProblemDetails>(StatusCodes.Status400BadRequest)
            .AllowAnonymous();

        group.MapGet("/{userId:guid}/display-name", GetUserDisplayName)
            .WithName("GetUserDisplayName")
            .WithSummary("Get a user's display name by ID")
            .Produces<string>(StatusCodes.Status200OK)
            .AllowAnonymous();

        return group;
    }

    private static async Task<IResult> Signup(
        [FromBody] SignupRequest request,
        IMediator mediator,
        CancellationToken ct)
    {
        try
        {
            var command = new SignupCommand(
                request.Username,
                request.Email,
                request.FullName,
                request.Password
            );

            var response = await mediator.SendAsync(command, ct);
            return Results.Ok(response);
        }
        catch (InvalidOperationException ex)
        {
            return Results.Problem(
                title: "Signup Failed",
                detail: ex.Message,
                statusCode: StatusCodes.Status400BadRequest
            );
        }
    }

    private static async Task<IResult> GetMe(
        ClaimsPrincipal user,
        IMediator mediator,
        CancellationToken ct)
    {
        var userIdClaim = user.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (userIdClaim is null || !Guid.TryParse(userIdClaim, out var userId))
        {
            return Results.Unauthorized();
        }

        try
        {
            var query = new GetMeQuery(userId);
            var response = await mediator.QueryAsync(query, ct);
            return Results.Ok(response);
        }
        catch (InvalidOperationException ex)
        {
            return Results.Problem(
                title: "User Not Found",
                detail: ex.Message,
                statusCode: StatusCodes.Status404NotFound
            );
        }
    }

    private static async Task<IResult> UpdateProfile(
        [FromBody] UpdateProfileRequest request,
        ClaimsPrincipal user,
        IMediator mediator,
        CancellationToken ct)
    {
        var userIdClaim = user.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (userIdClaim is null || !Guid.TryParse(userIdClaim, out var userId))
        {
            return Results.Unauthorized();
        }

        try
        {
            var command = new UpdateProfileCommand(
                userId,
                request.FullName,
                request.JobTitle,
                request.AvatarUrl,
                request.PhoneNumber,
                request.Bio,
                request.PreferredLanguage,
                request.Timezone
            );

            var response = await mediator.SendAsync(command, ct);
            return Results.Ok(response);
        }
        catch (InvalidOperationException ex)
        {
            return Results.Problem(
                title: "Profile Update Failed",
                detail: ex.Message,
                statusCode: StatusCodes.Status400BadRequest
            );
        }
    }

    private static async Task<IResult> UpdateUser(
        Guid userToUpdateId,
        [FromBody] UpdateUserRequest request,
        ClaimsPrincipal user,
        IMediator mediator,
        CancellationToken ct)
    {
        var userIdClaim = user.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (userIdClaim is null || !Guid.TryParse(userIdClaim, out var currentUserId))
        {
            return Results.Unauthorized();
        }

        try
        {
            var command = new UpdateUserCommand(
                currentUserId,
                userToUpdateId,
                request.Password
            );

            var response = await mediator.SendAsync(command, ct);
            return Results.Ok(response);
        }
        catch (InvalidOperationException ex)
        {
            return Results.Problem(
                title: "User Update Failed",
                detail: ex.Message,
                statusCode: StatusCodes.Status404NotFound
            );
        }
    }

    private static async Task<IResult> ValidateUser(
        [FromQuery] string token,
        IMediator mediator,
        CancellationToken ct)
    {
        try
        {
            var command = new ValidateUserCommand(token);
            var response = await mediator.SendAsync(command, ct);
            return Results.Ok(response);
        }
        catch (NotImplementedException ex)
        {
            return Results.Problem(
                title: "Feature Not Implemented",
                detail: ex.Message,
                statusCode: StatusCodes.Status501NotImplemented
            );
        }
        catch (InvalidOperationException ex)
        {
            return Results.Problem(
                title: "Validation Failed",
                detail: ex.Message,
                statusCode: StatusCodes.Status400BadRequest
            );
        }
    }

    private static async Task<IResult> GetUserDisplayName(
        Guid userId,
        IMediator mediator,
        CancellationToken ct)
    {
        var query = new GetUserDisplayNameQuery(userId);
        var displayName = await mediator.QueryAsync(query, ct);
        return Results.Ok(displayName);
    }
}
