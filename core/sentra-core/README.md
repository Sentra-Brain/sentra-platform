# sentra-core

Shared logic for Sentra Brain services.

## Structure
```
sentra-core/
├── sentra_core/
│   ├── domain/                # Domain layer: business logic and entities
│   │   ├── constants/         # Domain-specific constants
│   │   ├── entities/          # Core domain entities (e.g., user, organization, event)
│   │   ├── enums/             # Enumerations for domain models
│   │   ├── repository/        # Domain repository interfaces
│   │   ├── services/          # Domain services and business rules
│   │   ├── __init__.py
│   │   ├── role.py            # Example domain entity or logic
│   ├── core/                  # Core models, exceptions, logging
│   ├── infra/                 # Infrastructure: database, external services
│   ├── __init__.py
│   └── model/                 # Shared models (if any)
├── tests/                     # Unit and integration tests
├── pyproject.toml             # Build system and dependencies
├── README.md
└── ...
```

- `sentra_core/domain/`: Domain layer containing business logic and entities
    - `constants/`: Domain-specific constants
    - `entities/`: Core domain entities (e.g., user, organization, event)
    - `enums/`: Enumerations for domain models
    - `repository/`: Domain repository interfaces
    - `services/`: Domain services and business rules
    - `role.py`: Example domain entity or logic

- `sentra_core/core/`: Core models, exceptions, logging
- `sentra_core/infra/`: Infrastructure: database, external services
- `sentra_core/model/`: Shared models (if any)
- `tests/`: Unit and integration tests
- `pyproject.toml`: Build system and dependencies
