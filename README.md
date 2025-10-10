# WebCat MCP Server

**Web search and content extraction for AI models via Model Context Protocol (MCP)**

[![Version](https://img.shields.io/badge/version-2.3.2-blue.svg)](https://github.com/Kode-Rex/webcat)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-multi--platform-blue.svg)](https://hub.docker.com/r/tmfrisinger/webcat)

## Quick Start

### Docker (Recommended)

```bash
# Run with Docker (no setup required)
docker run -p 8000:8000 tmfrisinger/webcat:latest

# With Serper API key for premium search
docker run -p 8000:8000 -e SERPER_API_KEY=your_key tmfrisinger/webcat:latest

# With authentication enabled
docker run -p 8000:8000 -e WEBCAT_API_KEY=your_token tmfrisinger/webcat:latest
```

**Supports:** linux/amd64, linux/arm64 (Intel/AMD, Apple Silicon, AWS Graviton)

### Local Development

```bash
cd docker
python -m pip install -e ".[dev]"

# Start MCP server with auto-reload
make dev

# Or run directly
python mcp_server.py
```

## What is WebCat?

WebCat is an **MCP (Model Context Protocol) server** that provides AI models with:
- 🔍 **Web Search** - Serper API (premium) or DuckDuckGo (free fallback)
- 📄 **Content Extraction** - Serper scrape API (premium) or Trafilatura (free fallback)
- 🌐 **Modern HTTP Transport** - Streamable HTTP with JSON-RPC 2.0
- 🐳 **Multi-Platform Docker** - Works on Intel, ARM, and Apple Silicon
- 🎯 **Composite Tool** - Single SERPER_API_KEY enables both search + scraping

Built with **FastMCP**, **Serper.dev**, and **Trafilatura** for seamless AI integration.

## Features

- ✅ **Optional Authentication** - Bearer token auth when needed, or run without (v2.3.1)
- ✅ **Composite Search Tool** - Single Serper API key enables both search + scraping
- ✅ **Automatic Fallback** - Search: Serper → DuckDuckGo | Scraping: Serper → Trafilatura
- ✅ **Premium Scraping** - Serper's optimized infrastructure for fast, clean content extraction
- ✅ **Smart Content Extraction** - Returns markdown with preserved document structure
- ✅ **MCP Compliant** - Works with Claude Desktop, LiteLLM, and other MCP clients
- ✅ **Parallel Processing** - Fast concurrent scraping
- ✅ **Multi-Platform Docker** - Linux (amd64/arm64) support

## Installation & Usage

### Docker Deployment

```bash
# Quick start - no configuration needed
docker run -p 8000:8000 tmfrisinger/webcat:latest

# With environment variables
docker run -p 8000:8000 \
  -e SERPER_API_KEY=your_key \
  -e WEBCAT_API_KEY=your_token \
  tmfrisinger/webcat:latest

# Using docker-compose
cd docker
docker-compose up
```

### Local Development

```bash
cd docker
python -m pip install -e ".[dev]"

# Configure environment (optional)
echo "SERPER_API_KEY=your_key" > .env

# Development mode with auto-reload
make dev        # Start MCP server with auto-reload

# Production mode
make mcp        # Start MCP server
```

## Available Endpoints

| Endpoint | Description |
|----------|-------------|
| `http://localhost:8000/health` | 💗 Health check |
| `http://localhost:8000/status` | 📊 Server status |
| `http://localhost:8000/mcp` | 🛠️ MCP protocol endpoint (Streamable HTTP with JSON-RPC 2.0) |

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SERPER_API_KEY` | *(none)* | Serper API key for premium search (optional, falls back to DuckDuckGo if not set) |
| `PERPLEXITY_API_KEY` | *(none)* | Perplexity API key for deep research tool (optional, get at https://www.perplexity.ai/settings/api) |
| `WEBCAT_API_KEY` | *(none)* | Bearer token for authentication (optional, if set all requests must include `Authorization: Bearer <token>`) |
| `PORT` | `8000` | Server port |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_DIR` | `/tmp` | Log file directory |
| `MAX_CONTENT_LENGTH` | `1000000` | Maximum characters to return per scraped article |

### Get API Keys

**Serper API (for web search + scraping):**
1. Visit [serper.dev](https://serper.dev)
2. Sign up for free tier (2,500 searches/month + scraping)
3. Copy your API key
4. Add to `.env` file: `SERPER_API_KEY=your_key`
5. **Note:** One API key enables both search AND content scraping!

**Perplexity API (for deep research):**
1. Visit [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api)
2. Sign up and get your API key
3. Copy your API key
4. Add to `.env` file: `PERPLEXITY_API_KEY=your_key`

### Enable Authentication (Optional)

To require bearer token authentication for all MCP tool calls:

1. Generate a secure random token: `openssl rand -hex 32`
2. Add to `.env` file: `WEBCAT_API_KEY=your_token`
3. Include in all requests: `Authorization: Bearer your_token`

**Note:** If `WEBCAT_API_KEY` is not set, no authentication is required.

## MCP Tools

WebCat exposes these tools via MCP:

| Tool | Description | Parameters |
|------|-------------|------------|
| `search` | Search web and extract content | `query: str`, `max_results: int` |
| `scrape_url` | Scrape specific URL | `url: str` |
| `health_check` | Check server health | *(none)* |
| `get_server_info` | Get server capabilities | *(none)* |

## Architecture

```
MCP Client (Claude, LiteLLM)
    ↓
FastMCP Server (Streamable HTTP with JSON-RPC 2.0)
    ↓
Authentication (optional bearer token)
    ↓
Search Decision
    ├─ Serper API (premium) → Serper Scrape API (premium)
    └─ DuckDuckGo (free)    → Trafilatura (free)
                                    ↓
                            Markdown Response
```

**Tech Stack:**
- **FastMCP** - MCP protocol implementation with modern HTTP transport
- **JSON-RPC 2.0** - Standard protocol for client-server communication
- **Serper API** - Google-powered search + optimized web scraping
- **Trafilatura** - Fallback content extraction (removes navigation/ads)
- **DuckDuckGo** - Free search fallback

## Testing

```bash
cd docker

# Run all unit tests
make test
# OR
python -m pytest tests/unit -v

# With coverage report
make test-coverage
# OR
python -m pytest tests/unit --cov=. --cov-report=term --cov-report=html

# CI-safe tests (no external dependencies)
python -m pytest -v -m "not integration"

# Run specific test file
python -m pytest tests/unit/services/test_content_scraper.py -v
```

**Current test coverage:** 70%+ across all modules (enforced in CI)

## Development

```bash
# First-time setup
make setup-dev   # Install all dependencies + pre-commit hooks

# Development workflow
make dev         # Start server with auto-reload
make format      # Auto-format code (Black + isort)
make lint        # Check code quality (flake8)
make test        # Run unit tests

# Before committing
make ci-fast     # Quick validation (~30 seconds)
# OR
make ci          # Full validation with security checks (~2-3 minutes)

# Code quality tools
make format-check   # Check formatting without changes
make security       # Run bandit security scanner
make audit          # Check dependency vulnerabilities
```

**Pre-commit Hooks:**
Hooks run automatically on `git commit` to ensure code quality. Install with `make setup-dev`.

## Project Structure

```
docker/
├── mcp_server.py          # Main MCP server (FastMCP)
├── cli.py                 # CLI interface for server modes
├── health.py              # Health check endpoint
├── api_tools.py           # API tooling utilities
├── clients/               # External API clients
│   ├── serper_client.py  # Serper API (search + scrape)
│   └── duckduckgo_client.py  # DuckDuckGo fallback
├── services/              # Core business logic
│   ├── search_service.py # Search orchestration
│   └── content_scraper.py # Serper scrape → Trafilatura fallback
├── tools/                 # MCP tool implementations
│   └── search_tool.py    # Search tool with auth
├── models/                # Pydantic data models
│   ├── domain/           # Domain entities (SearchResult, etc.)
│   └── responses/        # API response models
├── utils/                 # Shared utilities
│   └── auth.py           # Bearer token authentication
├── endpoints/             # FastAPI endpoints
├── tests/                 # Comprehensive test suite
│   ├── unit/             # Unit tests (mocked dependencies)
│   └── integration/      # Integration tests (external deps)
└── pyproject.toml         # Project config + dependencies
```

## Search Quality Comparison

| Feature | Serper API | DuckDuckGo |
|---------|------------|------------|
| **Cost** | Paid (free tier available) | Free |
| **Quality** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Good |
| **Coverage** | Comprehensive (Google-powered) | Standard |
| **Speed** | Fast | Fast |
| **Rate Limits** | 2,500/month (free tier) | None |

## Docker Multi-Platform Support

WebCat supports multiple architectures for broad deployment compatibility:

```bash
# Build locally for multiple platforms
cd docker
./build.sh  # Builds for linux/amd64 and linux/arm64

# Manual multi-platform build and push
docker buildx build --platform linux/amd64,linux/arm64 \
  -t tmfrisinger/webcat:2.3.2 \
  -t tmfrisinger/webcat:latest \
  -f Dockerfile --push .

# Verify multi-platform support
docker buildx imagetools inspect tmfrisinger/webcat:latest
```

**Automated Releases:**
Push a version tag to trigger automated multi-platform builds via GitHub Actions:
```bash
git tag v2.3.2
git push origin v2.3.2
```

## Limitations

- **Text-focused:** Optimized for article content, not multimedia
- **No JavaScript:** Cannot scrape dynamic JS-rendered content (uses static HTML)
- **PDF support:** Detection only, not full extraction
- **Python 3.11 required:** Not compatible with 3.10 or 3.12
- **External API limits:** Subject to Serper API rate limits (2,500/month free tier)

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure `make ci` passes
5. Submit a Pull Request

See [CLAUDE.md](CLAUDE.md) for development guidelines and architecture standards.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- **GitHub:** [github.com/Kode-Rex/webcat](https://github.com/Kode-Rex/webcat)
- **MCP Spec:** [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **Serper API:** [serper.dev](https://serper.dev)

---

**Version 2.3.2** | Built with FastMCP, FastAPI, Readability, and html2text
