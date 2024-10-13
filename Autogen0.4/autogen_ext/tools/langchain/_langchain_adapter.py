import asyncio
import inspect
from typing import Any, Callable, Dict, Tuple, Type, cast

from autogen_core.base import CancellationToken
from autogen_core.components.tools import BaseTool
from pydantic import BaseModel, Field, create_model
from pydantic.fields import FieldInfo

from langchain.tools import Tool as LangChainTool

FieldDefinition = Tuple[Type[Any], FieldInfo]
FieldsDict = Dict[str, FieldDefinition]


class LangChainToolAdapter(BaseTool[BaseModel, Any]):
    langchain_tool: LangChainTool
    _callable: Callable[..., Any]

    def __init__(self, langchain_tool: LangChainTool):
        self.langchain_tool = langchain_tool

        # Extract name and description
        name = langchain_tool.name
        description = langchain_tool.description or ""

        # Determine the callable method
        if hasattr(langchain_tool, "func") and callable(langchain_tool.func):
            assert langchain_tool.func is not None
            self._callable = langchain_tool.func
        elif hasattr(langchain_tool, "_run") and callable(langchain_tool._run):  # pyright: ignore
            self._callable = langchain_tool._run  # type: ignore
        else:
            raise AttributeError(
                f"The provided LangChain tool '{name}' does not have a callable 'func' or '_run' method."
            )

        # Determine args_type
        if langchain_tool.args_schema:  # pyright: ignore
            args_type = langchain_tool.args_schema  # pyright: ignore
        else:
            # Infer args_type from the callable's signature
            sig = inspect.signature(cast(Callable[..., Any], self._callable))
            fields = {
                k: (v.annotation, Field(...))
                for k, v in sig.parameters.items()
                if k != "self" and v.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
            }
            args_type = create_model(f"{name}Args", **fields)  # type: ignore
            # Note: type ignore is used due to a LangChain typing limitation

        # Ensure args_type is a subclass of BaseModel
        if not issubclass(args_type, BaseModel):
            raise ValueError(f"Failed to create a valid Pydantic v2 model for {name}")

        # Assume return_type as Any if not specified
        return_type: Type[Any] = object

        super().__init__(args_type, return_type, name, description)

    async def run(self, args: BaseModel, cancellation_token: CancellationToken) -> Any:
        # Prepare arguments
        kwargs = args.model_dump()

        # Determine if the callable is asynchronous
        if inspect.iscoroutinefunction(self._callable):
            result = await self._callable(**kwargs)
        else:
            # Run in a thread to avoid blocking the event loop
            result = await asyncio.to_thread(self._call_sync, kwargs)

        return result

    def _call_sync(self, kwargs: Dict[str, Any]) -> Any:
        return self._callable(**kwargs)
