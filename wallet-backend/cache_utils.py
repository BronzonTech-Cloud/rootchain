from functools import wraps
import time
from typing import Dict, Any, Optional, Callable

class TTLCache:
    def __init__(self, maxsize: int = 1000, ttl: int = 60):
        self.maxsize = maxsize
        self.ttl = ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
    
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            key = str(args) + str(kwargs)
            now = time.time()
            
            # Check if cached and not expired
            if key in self.cache:
                result, timestamp = self.cache[key]['result'], self.cache[key]['timestamp']
                if now - timestamp < self.ttl:
                    return result
            
            # Compute new result
            result = func(*args, **kwargs)
            
            # Store in cache
            self.cache[key] = {'result': result, 'timestamp': now}
            
            # Remove oldest if cache is full
            if len(self.cache) > self.maxsize:
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
                del self.cache[oldest_key]
            
            return result
        return wrapper 