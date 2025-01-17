import redis
import json
from typing import Any, Optional
from decimal import Decimal
import os

# Initialize Redis connection
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0,
    decode_responses=True
)

class RedisCache:
    @staticmethod
    def key_prefix(key: str) -> str:
        return f"rootchain:wallet:{key}"
    
    @staticmethod
    def serialize_value(value: Any) -> str:
        if isinstance(value, Decimal):
            return str(value)
        return json.dumps(value)
    
    @staticmethod
    def deserialize_value(value: str, value_type: type = str) -> Any:
        if value_type == Decimal:
            return Decimal(value)
        return json.loads(value)
    
    @classmethod
    def get(cls, key: str, value_type: type = str) -> Optional[Any]:
        try:
            value = redis_client.get(cls.key_prefix(key))
            if value is None:
                return None
            return cls.deserialize_value(value, value_type)
        except Exception:
            return None
    
    @classmethod
    def set(cls, key: str, value: Any, ttl: int = 60) -> bool:
        try:
            return redis_client.setex(
                cls.key_prefix(key),
                ttl,
                cls.serialize_value(value)
            )
        except Exception:
            return False
    
    @classmethod
    def delete(cls, key: str) -> bool:
        try:
            return redis_client.delete(cls.key_prefix(key)) > 0
        except Exception:
            return False
    
    @classmethod
    def get_balance_key(cls, chain_name: str, address: str) -> str:
        return f"balance:{chain_name}:{address}"
    
    @classmethod
    def get_gas_price_key(cls, chain_name: str) -> str:
        return f"gas_price:{chain_name}" 