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

builder.Build().Run();
