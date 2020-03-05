Prometheus is a Python template project with utilities like
- File system event (file / directory create, move, update, delete) monitor, and event routing to handlers
- Class library for in-memory file representations (base type for any file and file format specific sub classes csv, xlsx, xml etc...)
- Multi process, producer / consumer Redis task queues
- Base type for serializing and de-serializing instance to and from Redis
- Single file environment configuration through cli flag
- Extended Box client with built in rate limiting and other utils
- Store and retrieve Box API tokens from Redis
- Async event loop task worker limiter
- Async io HTTP client
- Async io Redis client
- Async io web API
- Async io file operations
- React web GUI
- Docker image builder
- Docker container orchestration
- Unit tests
- Dynamic import of modules, types and class instantiation during runtime
- HTTP request rate limiter
- Command line interface
- Logging configuration
- Slack log handler
- Twilio sms log handler


## Application Architecture ##

### Domain Model ###
Object oriented programming layer defining a conceptual model of the business domain that incorporates behaviour and state

Box Client
- boxsdk.Client - REST client interface into Box Platform APIs
- sentinel.box_client.SentinelBoxClient - Box Consulting boxsdk.Client subclass
- sentinel.http_client.RateLimiter - sentinel.box_client.SentinelBoxClient integrated rate limiting

Redis Client
- redis.Redis - client interface into Redis cache

Sentinel Type
- sentinel.bc_type.SentinelType - type for simple inspection of Python slot attributes assigned for memory efficient object instantiation

File System
- sentinel.file_system.files.bc_file.SentinelFile - sentinel.bc_type.SentinelType subclass. In memory representation of files with operating system and Box utilities

- sentinel.file_system.files.bc_file.YMLFile - sentinel.file_system.files.bc_file.BCFile subclass with yml file associated utilities
- sentinel.file_system.files.config_file.SentinelConfigFile - sentinel.file_system.files.bc_file.YMLFile subclass with configuration file associated utilities
 
- sentinel.file_system.files.csv_file.CSVFile - sentinel.file_system.files.bc_file.BCFile subclass with csv file associated utilities

### Managers ###
Functional programming layer to instantiate the domain model class library and manipulate state with custom logic

- sentinel.manager.redis_client.* - Redis query utilities

### Command Line Interface ###
Exposes the manager layer to users through the command line

- sentinel.cli.redis_client.* - Redis query utilities
- sentinel.cli.__main__ - CLI package entry point and module specific command registration

### Docker Container Orchestration ###
- docker-compose.yml - Docker container management through Docker Compose to run Redis as a container with networking configured for communication between Docker Engine and the host

### Test Suite ###
- test.test_* - Template pytest unit test that can be extended by KKR engineers to integrate test coverage
- test.conftest - Template test fixture
- pytest.ini - pytest configuration

### Python Virtual Environment ###
- env/* - Utility to create isolated Python environments with access to an interpreter with Sentinel specific dependencies installed

### Data ###
- data/* - Non executable application state

### Log ###
- data/configuration/*.yml -> log - Python logging dictionary configuration supporting multiple environments
- data/log/*.log -> Agent log files
- sentinel.log.SlackLogHandler - Log handler that KKR engineers can integrate into an environment specific log configuration for real time Slack alerts
- sentinel.log.SMSLogHandler - Log handler that KKR engineers can integrate into an environment specific log configuration for real time SMS alerts
