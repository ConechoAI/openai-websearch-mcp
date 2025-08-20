# OpenAI WebSearch MCP Server
[![Trust Score](https://archestra.ai/mcp-catalog/api/badge/quality/ConechoAI/openai-websearch-mcp)](https://archestra.ai/mcp-catalog/conechoai__openai-websearch-mcp)

This MCP server provides access to OpenAI's websearch functionality through the Model Context Protocol. It allows AI assistants to search the web during conversations with users, providing up-to-date information that may not be available in the assistant's training data. The server can be installed and configured for use with Claude.app or Zed editor.

## One click installation & Configuration

### Claude 

!!Can using this command auto update configure file（Recommend）
```bash
OPENAI_API_KEY=sk-xxxx uv run --with uv --with openai-websearch-mcp openai-websearch-mcp-install
```
sk-xxxx is your API key. You can get it from [openai's open platform](https://platform.openai.com/)

### Cursor
Conming soon

### Windsurf
Conming soon


## Available Tools

- `web_search` - Call openai websearch as tool.
  - Required arguments:
    - `type` (string): web_search_preview
    - `search_context_size` (string): High level guidance for the amount of context window space to use for the search. One of low, medium, or high. medium is the default.
    - `user_location` (object or null)
      - `type` (string): The type of location > approximation. Always approximate.
      - `city` (string): Free text input for the city of the user, e.g. San Francisco.
      - `country` (string): The two-letter ISO country code of the user, e.g. US.
      - `region` (string): Free text input for the region of the user, e.g. California.
      - `timezone` (string): The IANA timezone of the user, e.g. America/Los_Angeles.


## Manual installation and configuration

Please make sure `uvx` is installed before installation

Add to your Claude settings:


1、Using uvx

```json
"mcpServers": {
  "openai-websearch-mcp": {
    "command": "uvx",
    "args": ["openai-websearch-mcp"],
    "env": {
        "OPENAI_API_KEY": "your-api-key-here"
    }
  }
}
```

2、Using pip installation

1）install `openai-websearch-mcp` via pip:

```bash
pip install openai-websearch-mcp
```

2）modify your Claude settings

```json
"mcpServers": {
  "openai-websearch-mcp": {
    "command": "python",
    "args": ["-m", "openai_websearch_mcp"],
    "env": {
        "OPENAI_API_KEY": "your-api-key-here"
    }
  }
}
```

### Configure for Zed

Add to your Zed settings.json:

Using uvx

```json
"context_servers": [
  "openai-websearch-mcp": {
    "command": "uvx",
    "args": ["openai-websearch-mcp"],
    "env": {
        "OPENAI_API_KEY": "your-api-key-here"
    }
  }
],
```

Using pip installation

```json
"context_servers": {
  "openai-websearch-mcp": {
    "command": "python",
    "args": ["-m", "openai_websearch_mcp"],
    "env": {
        "OPENAI_API_KEY": "your-api-key-here"
    }
  }
},
```

## Debugging

You can use the MCP inspector to debug the server. For uvx installations:

```bash
npx @modelcontextprotocol/inspector uvx openai-websearch-mcp
```
