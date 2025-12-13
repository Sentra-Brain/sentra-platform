using Kommand.Abstractions;
using Microsoft.AspNetCore.Mvc;
using Sentra.Api.Features.Auth;
using Sentra.Api.Features.Auth.Commands;

namespace Sentra.Api.Features.Auth;

/// <summary>
/// Authentication endpoints for login and token refresh.
/// </summary>
public static class AuthEndpoints
{
    public static RouteGroupBuilder MapAuthEndpoints(this WebApplication app)
    {
        var group = app.MapGroup("/auth")
            .WithTags("Authentication");

        group.MapPost("/token", Login)
            .WithName("Login")
            .WithSummary("Authenticate user and generate tokens")
            .Produces<LoginResponse>(StatusCodes.Status200OK)
            .Produces<ProblemDetails>(StatusCodes.Status401Unauthorized)
            .AllowAnonymous();

        group.MapPost("/refresh", RefreshToken)
            .WithName("RefreshToken")
            .WithSummary("Refresh access token using refresh token")
            .Produces<RefreshTokenResponse>(StatusCodes.Status200OK)
            .Produces<ProblemDetails>(StatusCodes.Status401Unauthorized)
            .AllowAnonymous();

        return group;
    }

    private static async Task<IResult> Login(
        [FromBody] LoginRequest request,
        IMediator mediator,
        CancellationToken ct)
    {
        try
        {
            var command = new LoginCommand(request.EmailOrUsername, request.Password);
            var response = await mediator.SendAsync(command, ct);
            return Results.Ok(response);
        }
        catch (UnauthorizedAccessException ex)
        {
            return Results.Problem(
                title: "Authentication Failed",
                detail: ex.Message,
                statusCode: StatusCodes.Status401Unauthorized
            );
        }
    }

    private static async Task<IResult> RefreshToken(
        [FromBody] RefreshRequest request,
        IMediator mediator,
        CancellationToken ct)
    {
        try
        {
            var command = new RefreshTokenCommand(request.RefreshToken);
            var response = await mediator.SendAsync(command, ct);
            return Results.Ok(response);
        }
        catch (UnauthorizedAccessException ex)
        {
            return Results.Problem(
                title: "Token Refresh Failed",
                detail: ex.Message,
                statusCode: StatusCodes.Status401Unauthorized
            );
        }
    }
}
