using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.OpenApi;
using Microsoft.OpenApi;

namespace Sentra.Api.OpenApi;

internal sealed class BearerSecuritySchemeTransformer(
    IAuthenticationSchemeProvider authenticationSchemeProvider
) : IOpenApiDocumentTransformer
{
    public async Task TransformAsync(
        OpenApiDocument document,
        OpenApiDocumentTransformerContext context,
        CancellationToken cancellationToken)
    {
        // Only add if Bearer is actually configured
        var schemes = await authenticationSchemeProvider.GetAllSchemesAsync();
        if (!schemes.Any(s => s.Name == "Bearer"))
            return;

        document.Components ??= new OpenApiComponents();
        document.Components.SecuritySchemes ??= new Dictionary<string, IOpenApiSecurityScheme>();       

        //
        // 1. OAuth2 Password flow (to force Swagger UI to show a login form)
        //
        document.Components.SecuritySchemes["OAuthPassword"] =
            new OpenApiSecurityScheme
            {
                Type = SecuritySchemeType.OAuth2,
                Description = "Authenticate using username and password (mapped to /auth/token).",
                Flows = new OpenApiOAuthFlows
                {
                    Password = new OpenApiOAuthFlow
                    {
                        TokenUrl = new Uri("/auth/token", UriKind.Relative),
                        Scopes = new Dictionary<string, string>
                        {
                            { "api", "Access the Sentra API" }
                        }
                    }
                }
            };

        //
        // 1. Bearer (your current scheme - leave untouched)
        //
        document.Components.SecuritySchemes["Bearer"] = new OpenApiSecurityScheme
        {
            Type = SecuritySchemeType.Http,
            Scheme = "bearer",
            In = ParameterLocation.Header,
            BearerFormat = "JWT",
            Description = "JWT Bearer authentication"
        };

        //
        // 3. Apply security requirements to every operation
        //
        foreach (var path in document.Paths.Values)
        {
            if (path?.Operations == null)
                continue;

            foreach (var operation in path.Operations.Values)
            {
                operation.Security ??= new List<OpenApiSecurityRequirement>();

                // Bearer
                operation.Security.Add(new OpenApiSecurityRequirement
                {
                    [new OpenApiSecuritySchemeReference("Bearer", document)] = []
                });

                // OAuth password flow
                operation.Security.Add(new OpenApiSecurityRequirement
                {
                    [new OpenApiSecuritySchemeReference("OAuthPassword", document)] = new List<string> { "api" }
                });
            }
        }
    }
}
