import json
from enum import Enum
from typing import Any, cast

from autogen_core.base import AgentId


class LLMCallEvent:
    def __init__(self, *, prompt_tokens: int, completion_tokens: int, **kwargs: Any) -> None:
        """To be used by model clients to log the call to the LLM.

        Args:
            prompt_tokens (int): Number of tokens used in the prompt.
            completion_tokens (int): Number of tokens used in the completion.

        Example:

            .. code-block:: python

                from autogen_core.application.logging import LLMCallEvent, EVENT_LOGGER_NAME

                logger = logging.getLogger(EVENT_LOGGER_NAME)
                logger.info(LLMCallEvent(prompt_tokens=10, completion_tokens=20))

        """
        self.kwargs = kwargs
        self.kwargs["prompt_tokens"] = prompt_tokens
        self.kwargs["completion_tokens"] = completion_tokens
        self.kwargs["type"] = "LLMCall"

    @property
    def prompt_tokens(self) -> int:
        return cast(int, self.kwargs["prompt_tokens"])

    @property
    def completion_tokens(self) -> int:
        return cast(int, self.kwargs["completion_tokens"])

    # This must output the event in a json serializable format
    def __str__(self) -> str:
        return json.dumps(self.kwargs)


class MessageKind(Enum):
    DIRECT = 1
    PUBLISH = 2
    RESPOND = 3


class DeliveryStage(Enum):
    SEND = 1
    DELIVER = 2


class MessageEvent:
    def __init__(
        self,
        *,
        payload: Any,
        sender: AgentId | None,
        receiver: AgentId | None,
        kind: MessageKind,
        delivery_stage: DeliveryStage,
        **kwargs: Any,
    ) -> None:
        self.kwargs = kwargs
        self.kwargs["payload"] = payload
        self.kwargs["sender"] = None if sender is None else str(sender)
        self.kwargs["receiver"] = None if receiver is None else str(receiver)
        self.kwargs["kind"] = kind
        self.kwargs["delivery_stage"] = delivery_stage
        self.kwargs["type"] = "Message"

    @property
    def prompt_tokens(self) -> int:
        return cast(int, self.kwargs["prompt_tokens"])

    @property
    def completion_tokens(self) -> int:
        return cast(int, self.kwargs["completion_tokens"])

    # This must output the event in a json serializable format
    def __str__(self) -> str:
        return json.dumps(self.kwargs)
