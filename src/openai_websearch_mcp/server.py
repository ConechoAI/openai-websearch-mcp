from pydantic import BaseModel
from typing import Literal
from httmcp import HTTMCP
from openai import OpenAI
from pydantic_extra_types.timezone_name import TimeZoneName
from pydantic import BaseModel

mcp = HTTMCP(
    name="openai_web_search",
    instructions="This MCP server provides access to OpenAI's websearch functionality through the Model Context Protocol."
)

class UserLocation(BaseModel):
    type: Literal["approximate"] = "approximate"
    city: str
    country: str = None
    region: str = None
    timezone: TimeZoneName


@mcp.tool(
    name="web_search",
    description=" It allows AI assistants to search the web during conversations with users",
)
def web_search(
    input: str,
    model: Literal["gpt-4o", "gpt-4o-mini"] = "gpt-4o-mini",
    type: Literal["web_search_preview", "web_search_preview_2025_03_11"] = "web_search_preview",
    search_context_size: Literal["low", "medium", "high"] = "medium",
    user_location: UserLocation = None,
) -> list[str]:
    client = OpenAI()
    response = client.responses.create(
        model=model,
        tools=[
            {
                "type": type,
                "search_context_size": search_context_size,
                "user_location": user_location.model_dump() if user_location else None,
            }
        ],
        input=input,
    )
    return response.output_text

