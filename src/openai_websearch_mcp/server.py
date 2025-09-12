from pydantic import BaseModel, Field
from typing import Literal, Optional, Annotated
from mcp.server.fastmcp import FastMCP
from openai import OpenAI
from pydantic_extra_types.timezone_name import TimeZoneName
from pydantic import BaseModel
import os

mcp = FastMCP(
    name="OpenAI Web Search",
    instructions="This MCP server provides access to OpenAI's websearch functionality through the Model Context Protocol."
)

class UserLocation(BaseModel):
    type: Literal["approximate"] = "approximate"
    city: str
    country: str = None
    region: str = None
    timezone: TimeZoneName


@mcp.tool(
    name="openai_web_search",
    description="""OpenAI Web Search with reasoning models. 

For quick multi-round searches: Use 'gpt-5-mini' with reasoning_effort='low' for fast iterations.

For deep research: Use 'gpt-5' with reasoning_effort='medium' or 'high'. 
The result is already multi-round reasoned, so agents don't need continuous iterations.

Supports: gpt-4o (no reasoning), gpt-5/gpt-5-mini/gpt-5-nano, o3/o4-mini (with reasoning).""",
)
def openai_web_search(
    input: Annotated[str, Field(description="The search query or question to search for")],
    model: Annotated[Optional[Literal["gpt-4o", "gpt-4o-mini", "gpt-5", "gpt-5-mini", "gpt-5-nano", "o3", "o4-mini"]], 
                     Field(description="AI model to use. Defaults to OPENAI_DEFAULT_MODEL env var or gpt-5-mini")] = None,
    reasoning_effort: Annotated[Optional[Literal["low", "medium", "high", "minimal"]], 
                                Field(description="Reasoning effort level for supported models (gpt-5, o3, o4-mini). Default: low for gpt-5-mini, medium for others")] = None,
    type: Annotated[Literal["web_search_preview", "web_search_preview_2025_03_11"], 
                    Field(description="Web search API version to use")] = "web_search_preview",
    search_context_size: Annotated[Literal["low", "medium", "high"], 
                                   Field(description="Amount of context to include in search results")] = "medium",
    user_location: Annotated[Optional[UserLocation], 
                            Field(description="Optional user location for localized search results")] = None,
) -> str:
    # 从环境变量读取默认模型，如果没有则使用 gpt-5-mini
    if model is None:
        model = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-5-mini")
    
    client = OpenAI()
    
    # 判断是否为推理模型
    reasoning_models = ["gpt-5", "gpt-5-mini", "gpt-5-nano", "o3", "o4-mini"]
    
    # 构建请求参数
    request_params = {
        "model": model,
        "tools": [
            {
                "type": type,
                "search_context_size": search_context_size,
                "user_location": user_location.model_dump() if user_location else None,
            }
        ],
        "input": input,
    }
    
    # 对推理模型设置智能默认值
    if model in reasoning_models:
        if reasoning_effort is None:
            # gpt-5-mini 默认使用 low，其他推理模型默认 medium
            if model == "gpt-5-mini":
                reasoning_effort = "low"  # 快速搜索
            else:
                reasoning_effort = "medium"  # 深度研究
        request_params["reasoning"] = {"effort": reasoning_effort}
    
    response = client.responses.create(**request_params)
    return response.output_text

