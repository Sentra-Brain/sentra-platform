using Microsoft.OpenApi;

namespace Sentra.Api.OpenApi;

public static class SentraOpenApiConfig
{
    public const string AppName = "sentra_brain_api";
    public const string Title = "Sentra Brain API";
    public const string Description = "API for Sentra Brain platform.";
    public const string Version = "0.2.0";

    public static readonly OpenApiContact Contact = new()
    {
        Name = "Sentra Brain Team",
        Email = "juan@jgcarmona.com"
    };

    public static readonly OpenApiLicense License = new()
    {
        Name = "AGPLv3",
        Url = new Uri("https://www.gnu.org/licenses/agpl-3.0.en.html")
    };
}
