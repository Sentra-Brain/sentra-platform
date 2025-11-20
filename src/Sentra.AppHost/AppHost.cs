var builder = DistributedApplication.CreateBuilder(args);

// -------------------------
// Secrets (secure parameters)
// -------------------------

var mongoUser = builder.AddParameter("mongo-user");
var mongoPass = builder.AddParameter("mongo-password", secret: true);

var pgUser = builder.AddParameter("postgres-user");
var pgPass = builder.AddParameter("postgres-password", secret: true);

var rabbitUser = builder.AddParameter("rabbit-user");
var rabbitPass = builder.AddParameter("rabbit-password", secret: true);

// -------------------------
// Constants
// -------------------------
var dataFolder = "../../data";
var dbNameSql = "sentra-brain-sql";
var dbNameNoSql = "sentra-brain-nosql";

// ============================================================
// MongoDB
// ============================================================

var mongo = builder.AddMongoDB("mongo", userName: mongoUser, password: mongoPass)
    .WithLifetime(ContainerLifetime.Persistent)
    .WithDataBindMount(source: $"{dataFolder}/mongo", isReadOnly: false);

var mongoDb = mongo.AddDatabase(dbNameNoSql);


// ============================================================
// PostgreSQL
// ============================================================

var postgres = builder.AddPostgres("postgres", pgUser, pgPass)
    .WithLifetime(ContainerLifetime.Persistent)
    .WithDataBindMount(source: $"{dataFolder}/postgres", isReadOnly: false)
    .WithPgWeb(pgweb => pgweb.WithHostPort(5050));

var sentraDb = postgres.AddDatabase(dbNameSql);

// ============================================================
// Chroma Vector Database
// ============================================================

var chroma = builder.AddContainer("chroma", "ghcr.io/chroma-core/chroma", "latest")
    .WithHttpEndpoint(targetPort: 8000)
    .WithBindMount(Path.Combine(dataFolder, "chroma"), "/data") 
    .WithContainerFiles(sourcePath: $"../Sentra.Infrastructure.ChromaDb/config.yaml", destinationPath: "/aspire")
    .WithEnvironment("CHROMA_CONFIG", "/aspire/config.yaml")
    .WithLifetime(ContainerLifetime.Persistent);

// ============================================================
// RabbitMQ
// ============================================================

var rabbit = builder.AddRabbitMQ("rabbitmq", rabbitUser, rabbitPass)
    .WithLifetime(ContainerLifetime.Persistent)
    .WithManagementPlugin()
    .WithDataBindMount(source: $"{dataFolder}/rabbitmq", isReadOnly: false);


// ============================================================
// Docker MCP Gateway
// ============================================================
var mcpGateway = builder
    .AddContainer("mcp-gateway", "docker/mcp-gateway", "latest")
    .WithContainerName("mcp_gateway")
    .WithBindMount("/var/run/docker.sock", "/var/run/docker.sock")
    .WithBindMount(
        Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
            ".docker/mcp"
        ),
        "/mcp"
    )
    .WithArgs(
        "--catalog=/mcp/catalogs/docker-mcp.yaml",
        "--config=/mcp/config.yaml",
        "--registry=/mcp/registry.yaml",
        "--secrets=docker-desktop",
        "--watch=true",
        "--transport=streaming",
        "--port=8811"
    )
    .WithEndpoint(
        port: 8811,
        targetPort: 8811,
        scheme: "tcp",
        name: "mcp",
        env: null,
        isProxied: false,
        isExternal: true
    )
    .WithLifetime(ContainerLifetime.Persistent);




// ============================================================
// API Service
// ============================================================

var api = builder.AddProject<Projects.Sentra_Api>("sentra-api")
    .WithHttpHealthCheck("/health")
    .WithReference(mongoDb).WaitFor(mongoDb)
    .WithReference(sentraDb).WaitFor(sentraDb)
    .WithReference(rabbit).WaitFor(rabbit);



// ============================================================
// Sentra Web
// ============================================================

builder.AddNpmApp("sentra-web", "../Sentra.Web")
    .WithReference(api).WaitFor(api)
    .WithEnvironment("BROWSER", "none")
    .WithHttpEndpoint(env: "VITE_PORT")
    .WithExternalHttpEndpoints()
    .PublishAsDockerFile();

// ============================================================
// Sentra Rag Worker
// ============================================================

#pragma warning disable ASPIREHOSTINGPYTHON001 // Type is for evaluation purposes only and is subject to change or removal in future updates. Suppress this diagnostic to proceed.
var pythonapp = builder.AddPythonApp("sentra-rag-worker", "../Sentra.Rag.Worker", "sentra_rag_worker/main.py")
       .WithHttpEndpoint(env: "PORT")
       .WithExternalHttpEndpoints();
#pragma warning restore ASPIREHOSTINGPYTHON001

builder.Build().Run();
