import json
import sys
import getpass
from pathlib import Path
from typing import Optional, Dict
import logging
import sys
import os
import platform
import typer
from shutil import which
from openai import OpenAI


logger = logging.getLogger(__file__)

app = typer.Typer(
    name="openapi-websearch-mcp",
    help="openapi-websearch-mcp install tools",
    add_completion=False,
    no_args_is_help=True,  # Show help if no args provided
)



def get_claude_config_path() -> Path | None:
    """Get the Claude config directory based on platform."""
    if sys.platform == "win32":
        path = Path(Path.home(), "AppData", "Roaming", "Claude")
    elif sys.platform == "darwin":
        path = Path(Path.home(), "Library", "Application Support", "Claude")
    else:
        return None

    if path.exists():
        return path
    return None


def update_claude_config(
    server_name: str,
    command: str,
    args: list[str],
    *,
    env_vars: Optional[Dict[str, str]] = None,
) -> bool:
    """Add or update a FastMCP server in Claude's configuration.
    """
    config_dir = get_claude_config_path()
    if not config_dir:
        raise RuntimeError(
            "Claude Desktop config directory not found. Please ensure Claude Desktop "
            "is installed and has been run at least once to initialize its configuration."
        )

    config_file = config_dir / "claude_desktop_config.json"
    if not config_file.exists():
        try:
            config_file.write_text("{}")
        except Exception as e:
            logger.error(
                "Failed to create Claude config file",
                extra={
                    "error": str(e),
                    "config_file": str(config_file),
                },
            )
            return False

    try:
        config = json.loads(config_file.read_text())
        if "mcpServers" not in config:
            config["mcpServers"] = {}

        # Always preserve existing env vars and merge with new ones
        if (
            server_name in config["mcpServers"]
            and "env" in config["mcpServers"][server_name]
        ):
            existing_env = config["mcpServers"][server_name]["env"]
            if env_vars:
                # New vars take precedence over existing ones
                env_vars = {**existing_env, **env_vars}
            else:
                env_vars = existing_env

        server_config = {
            "command": command,
            "args": args,
        }

        # Add environment variables if specified
        if env_vars:
            server_config["env"] = env_vars

        config["mcpServers"][server_name] = server_config

        config_file.write_text(json.dumps(config, indent=2))
        logger.info(
            f"Added server '{server_name}' to Claude config",
            extra={"config_file": str(config_file)},
        )
        return True
    except Exception as e:
        logger.error(
            "Failed to update Claude config",
            extra={
                "error": str(e),
                "config_file": str(config_file),
            },
        )
        return False


@app.command()
def install() -> None:
    """Install a current server in the Claude desktop app.
    """

    name = "openai-websearch-mcp"

    env_dict = {}
    local_bin = Path(Path.home(), ".local", "bin")
    pyenv_shims = Path(Path.home(), ".pyenv", "shims")
    path = os.environ['PATH']
    python_version = platform.python_version()
    python_bin = Path(Path.home(), "Library", "Python", python_version, "bin")
    if sys.platform == "win32":
        env_dict["PATH"] = f"{local_bin};{pyenv_shims};{python_bin};{path}"
    else:
        env_dict["PATH"] = f"{local_bin}:{pyenv_shims}:{python_bin}:{path}"

    api_key = os.environ['OPENAI_API_KEY'] if "OPENAI_API_KEY" in os.environ else ""
    while api_key == "":
        api_key = getpass.getpass("Enter your OpenAI API key: ")
        if api_key != "":
            client = OpenAI(api_key=api_key)
            try:
                client.models.list()
            except Exception as e:
                logger.error(f"Failed to authenticate with OpenAI API: {str(e)}")
                api_key = ""

    env_dict["OPENAI_API_KEY"] = api_key
    
    # 添加默认模型配置（可选）
    default_model = os.environ.get("OPENAI_DEFAULT_MODEL", "gpt-5-mini")
    env_dict["OPENAI_DEFAULT_MODEL"] = default_model

    uv = which('uvx', path=env_dict['PATH'])
    command = uv if uv else "uvx"
    args = [name]

    # print("------------update_claude_config", command, args, env_dict)

    if update_claude_config(
        name,
        command,
        args,
        env_vars=env_dict,
    ):
        logger.info(f"Successfully installed {name} in Claude app")
    else:
        logger.error(f"Failed to install {name} in Claude app")
        sys.exit(1)
