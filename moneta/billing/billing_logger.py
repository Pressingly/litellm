from prisma import Prisma
from litellm.integrations.custom_logger import CustomLogger
from litellm.types.utils import ModelResponse
import time
import uuid
import httpx
import json
import os
from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    List,
    Literal,
    Optional,
    Tuple,
    Dict,
    Union,
)

import traceback
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
)

from pydantic import BaseModel
from fastapi import HTTPException

from litellm.caching.caching import DualCache
from litellm.proxy._types import UserAPIKeyAuth
from litellm.types.integrations.argilla import ArgillaItem
from litellm.types.llms.openai import AllMessageValues, ChatCompletionRequest
from litellm.types.utils import (
    AdapterCompletionStreamWrapper,
    LLMResponseTypes,
    ModelResponse,
    ModelResponseStream,
    StandardCallbackDynamicParams,
    StandardLoggingPayload,
)
from litellm.proxy.db.prisma_client import PrismaWrapper

if TYPE_CHECKING:
    from opentelemetry.trace import Span as _Span

    Span = Union[_Span, Any]
else:
    Span = Any

from litellm.proxy.db.prisma_client import PrismaWrapper
# load os env variables
import os



print("BillingLogger module loaded - test key : sk-rhyYVtjl6D74tbbfqZafyg")    
class BillingLogger(CustomLogger):
    def __init__(self, message_logging: bool = True) -> None:
        print("BillingLogger module is being initialized") 
        super().__init__()
        self.lago_api_base = os.getenv("LAGO_API_BASE")
        self.lago_api_key = os.getenv("LAGO_API_KEY")
        self.lago_event_code = os.getenv("LAGO_API_EVENT_CODE")
        self.db = PrismaWrapper(original_prisma=Prisma(), iam_token_db_auth=False)
        

    def __del__(self):
        """Cleanup when the logger is destroyed"""
        if hasattr(self, 'prisma'):
            self.db.disconnect()

    
    async def async_pre_call_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        cache: DualCache,
        data: dict,
        call_type: Literal[
            "completion",
            "text_completion",
            "embeddings",
            "image_generation",
            "moderation",
            "audio_transcription",
            "pass_through_endpoint",
            "rerank",
        ],
    ) -> Optional[
        Union[Exception, str, dict]
    ]:  # raise exception if invalid, return a str for the user to receive - if rejected, or return a modified dictionary for passing into litellm
        print(" async_pre_call_hook - hi there")

        subscription_id = data["proxy_server_request"]["headers"].get("x-openwebui-subscription-id", "f708a03c-dbb8-4c12-a65f-d154994d6a7b")
        if not subscription_id:
            raise Exception("Missing subscription ID")
        
        if self.db.is_connected() is False:
            await self.db.connect()
        subscription = await self.db.moneta_lagosubscription.find_first(where={"id": subscription_id})

        if subscription and subscription.remaining_balance[0]["remaining_usage_units"] < 0:
            raise HTTPException(status_code=402, detail={"error": "insufficient_funds","message": "Your account has insufficient funds to proceed."})

    async def async_log_success_event(self, kwargs: Dict[str, Any], response_obj: ModelResponse, start_time: float, end_time: float):
        """
        After successful completion, send usage event to Lago and update subscription balance
        """
        # try:
        # Get subscription_id from headers
        subscription_id = kwargs.get("headers", {}).get("x-openwebui-subscription-id", "f708a03c-dbb8-4c12-a65f-d154994d6a7b")
        
        if not subscription_id:
            return

        # Get response cost from the response object
        response_cost = kwargs['standard_logging_object']['response_cost']
        if not response_cost:
            return

        # Prepare Lago event
        event_data = {
            "event": {
                "transaction_id": str(uuid.uuid4()),
                "external_subscription_id": subscription_id,
                "code": "credit_cents",  # TODO: Make this configurable
                "timestamp": int(time.time()),
                "properties": {
                    "credit_cents": response_cost * 100,
                    "with_remaining_usage": True
                }
            },
            "sync": True
        }

        # Send event to Lago
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.lago_api_base}/api/v1/events",
                headers={
                    "Authorization": f"Bearer {self.lago_api_key}",
                    "Content-Type": "application/json"
                },
                json=event_data
            )
            response.raise_for_status()

            subscription_remaining_usage = response.json().get("event", {}).get("subscription_remaining_usage", {})
            if subscription_remaining_usage:
                await self.update_subscription_balance(subscription_id, subscription_remaining_usage)

    
    async def update_subscription_balance(self, subscription_id: str, remaining_balance: Any):
        data = {
            "id": subscription_id,
            "status": "active",
            "balance_threshold": json.dumps({}),
            "remaining_balance":  json.dumps(remaining_balance)  # make sure it's a string if it's JSON
        }
        
        # TODO: implement optimistic locking
        # TODO: id & customer id is uuidv4 instead of TEXT.
        subscription = await self.db.moneta_lagosubscription.upsert(
            where={
                "id": subscription_id,
            },
            data= {
                "create": data,
                "update": {"remaining_balance": json.dumps(remaining_balance)}  # make sure it's a string if it's JSON
            },   
        )
        print(f"Upserted subscription: {subscription}")
        return None




billing_logger = BillingLogger()