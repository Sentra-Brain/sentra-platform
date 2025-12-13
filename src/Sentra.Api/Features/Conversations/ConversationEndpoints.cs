using System;
using System.Security.Claims;
using System.Threading;
using System.Threading.Tasks;
using Kommand.Abstractions;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using Sentra.Api.Features.Conversations.Commands;
using Sentra.Api.Features.Conversations.Queries;
using Sentra.Api.Features.Conversations;

namespace Sentra.Api.Features.Conversations;

public static class ConversationEndpoints
{
    public static void MapConversationEndpoints(this IEndpointRouteBuilder endpoints)
    {
        var group = endpoints.MapGroup("/conversations")
            .WithTags("Conversations")
            .RequireAuthorization();

        // POST /conversations - Create new conversation
        group.MapPost("/", CreateConversation)
            .WithName("CreateConversation")
            .WithSummary("Creates a new conversation for the current user")
            .Produces<CreateConversationResponse>(StatusCodes.Status201Created)
            .Produces(StatusCodes.Status401Unauthorized);

        // GET /conversations - Get all conversations for current user
        group.MapGet("/", GetAllConversations)
            .WithName("GetAllConversations")
            .WithSummary("Retrieves all conversations for the current user")
            .Produces<System.Collections.Generic.List<ConversationListItemResponse>>(StatusCodes.Status200OK)
            .Produces(StatusCodes.Status401Unauthorized);

        // GET /conversations/{id} - Get conversation by ID
        group.MapGet("/{conversationId:guid}", GetConversationById)
            .WithName("GetConversationById")
            .WithSummary("Retrieve a specific conversation by its ID")
            .Produces<ConversationResponse>(StatusCodes.Status200OK)
            .Produces(StatusCodes.Status404NotFound);

        // PUT /conversations/{id} - Update conversation
        group.MapPut("/{conversationId:guid}", UpdateConversation)
            .WithName("UpdateConversation")
            .WithSummary("Update title and description of a conversation")
            .Produces<UpdateConversationResponse>(StatusCodes.Status200OK)
            .Produces(StatusCodes.Status404NotFound);

        // PATCH /conversations/{id}/title - Generate title
        group.MapPatch("/{conversationId:guid}/title", GenerateTitle)
            .WithName("GenerateConversationTitle")
            .WithSummary("Generate or update conversation title using AI")
            .Produces<GenerateTitleResponse>(StatusCodes.Status200OK)
            .Produces(StatusCodes.Status404NotFound);

        // DELETE /conversations/{id} - Delete conversation
        group.MapDelete("/{conversationId:guid}", DeleteConversation)
            .WithName("DeleteConversation")
            .WithSummary("Delete a conversation")
            .Produces<DeleteConversationResponse>(StatusCodes.Status200OK)
            .Produces(StatusCodes.Status404NotFound);
    }

    private static async Task<IResult> CreateConversation(
        CreateConversationRequest request,
        ClaimsPrincipal user,
        IMediator mediator,
        CancellationToken ct)
    {
        var userIdClaim = user.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (string.IsNullOrEmpty(userIdClaim) || !Guid.TryParse(userIdClaim, out var userId))
        {
            return Results.Unauthorized();
        }

        try
        {
            var command = new CreateConversationCommand(userId, request.InitialPrompt);
            var response = await mediator.SendAsync(command, ct);
            return Results.Created($"/conversations/{response.Id}", response);
        }
        catch (Exception ex)
        {
            return Results.Problem(ex.Message);
        }
    }

    private static async Task<IResult> GetAllConversations(
        ClaimsPrincipal user,
        IMediator mediator,
        CancellationToken ct)
    {
        var userIdClaim = user.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (string.IsNullOrEmpty(userIdClaim) || !Guid.TryParse(userIdClaim, out var userId))
        {
            return Results.Unauthorized();
        }

        try
        {
            var query = new GetAllConversationsQuery(userId);
            var response = await mediator.QueryAsync(query, ct);
            return Results.Ok(response);
        }
        catch (Exception ex)
        {
            return Results.Problem(ex.Message);
        }
    }

    private static async Task<IResult> GetConversationById(
        Guid conversationId,
        ClaimsPrincipal user,
        IMediator mediator,
        CancellationToken ct)
    {
        var userIdClaim = user.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (string.IsNullOrEmpty(userIdClaim) || !Guid.TryParse(userIdClaim, out var userId))
        {
            return Results.Unauthorized();
        }

        try
        {
            var query = new GetConversationByIdQuery(conversationId, userId);
            var response = await mediator.QueryAsync(query, ct);
            return Results.Ok(response);
        }
        catch (InvalidOperationException ex)
        {
            return Results.NotFound(new { error = ex.Message });
        }
        catch (UnauthorizedAccessException)
        {
            return Results.Forbid();
        }
        catch (Exception ex)
        {
            return Results.Problem(ex.Message);
        }
    }

    private static async Task<IResult> UpdateConversation(
        Guid conversationId,
        UpdateConversationRequest request,
        ClaimsPrincipal user,
        IMediator mediator,
        CancellationToken ct)
    {
        var userIdClaim = user.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (string.IsNullOrEmpty(userIdClaim) || !Guid.TryParse(userIdClaim, out var userId))
        {
            return Results.Unauthorized();
        }

        try
        {
            var command = new UpdateConversationCommand(conversationId, userId, request.Title, request.Description);
            var response = await mediator.SendAsync(command, ct);
            return Results.Ok(response);
        }
        catch (InvalidOperationException ex)
        {
            return Results.NotFound(new { error = ex.Message });
        }
        catch (UnauthorizedAccessException)
        {
            return Results.Forbid();
        }
        catch (Exception ex)
        {
            return Results.Problem(ex.Message);
        }
    }

    private static async Task<IResult> GenerateTitle(
        Guid conversationId,
        ClaimsPrincipal user,
        IMediator mediator,
        CancellationToken ct)
    {
        var userIdClaim = user.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (string.IsNullOrEmpty(userIdClaim) || !Guid.TryParse(userIdClaim, out var userId))
        {
            return Results.Unauthorized();
        }

        try
        {
            var command = new GenerateTitleCommand(conversationId, userId);
            var response = await mediator.SendAsync(command, ct);
            return Results.Ok(response);
        }
        catch (InvalidOperationException ex)
        {
            return Results.NotFound(new { error = ex.Message });
        }
        catch (UnauthorizedAccessException)
        {
            return Results.Forbid();
        }
        catch (Exception ex)
        {
            return Results.Problem(ex.Message);
        }
    }

    private static async Task<IResult> DeleteConversation(
        Guid conversationId,
        ClaimsPrincipal user,
        IMediator mediator,
        CancellationToken ct)
    {
        var userIdClaim = user.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (string.IsNullOrEmpty(userIdClaim) || !Guid.TryParse(userIdClaim, out var userId))
        {
            return Results.Unauthorized();
        }

        try
        {
            var command = new DeleteConversationCommand(conversationId, userId);
            var response = await mediator.SendAsync(command, ct);
            return Results.Ok(response);
        }
        catch (InvalidOperationException ex)
        {
            return Results.NotFound(new { error = ex.Message });
        }
        catch (UnauthorizedAccessException)
        {
            return Results.Forbid();
        }
        catch (Exception ex)
        {
            return Results.Problem(ex.Message);
        }
    }
}
