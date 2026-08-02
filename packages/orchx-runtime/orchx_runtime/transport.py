import time
import httpx
import asyncio
from typing import Dict, Any, AsyncGenerator, Tuple
from datetime import datetime, timezone

class CircuitBreaker:
    """
    State-machine Circuit Breaker to prevent repeated requests to unhealthy providers.
    States: 'closed' (normal), 'open' (failing), 'half-open' (testing recovery).
    """
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.state = "closed"
        self.last_failure_time = 0.0

    def record_success(self):
        self.failures = 0
        self.state = "closed"

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = "open"

    def can_execute(self) -> bool:
        if self.state == "closed":
            return True
        if self.state == "open":
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = "half-open"
                return True
            return False
        if self.state == "half-open":
            return True # allow one test request
        return True

class TransportLayer:
    """
    HTTP client abstraction using httpx.AsyncClient.
    Manages connection pooling, retries, timeout, and telemetry collection.
    """
    def __init__(self, timeout: float = 60.0):
        self.client = httpx.AsyncClient(timeout=timeout)
        self.circuit_breaker = CircuitBreaker()

    async def execute(self, method: str, url: str, headers: Dict[str, str], json: Dict[str, Any] = None) -> Tuple[httpx.Response, Dict[str, float]]:
        """
        Executes an HTTP request and records telemetry.
        """
        if not self.circuit_breaker.can_execute():
            raise ConnectionError(f"Circuit Breaker is OPEN for {url}")
            
        telemetry = {
            "start_time": time.time(),
            "retry_count": 0,
            "http_status": 0
        }
        
        retries = 3
        backoff = 1.0
        
        for attempt in range(retries):
            try:
                response = await self.client.request(method, url, headers=headers, json=json)
                telemetry["http_status"] = response.status_code
                
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", backoff))
                    await asyncio.sleep(retry_after)
                    telemetry["retry_count"] += 1
                    backoff *= 2
                    continue
                    
                response.raise_for_status()
                self.circuit_breaker.record_success()
                telemetry["total_duration"] = (time.time() - telemetry["start_time"]) * 1000
                return response, telemetry
                
            except httpx.HTTPStatusError as e:
                self.circuit_breaker.record_failure()
                if attempt == retries - 1:
                    raise
                telemetry["retry_count"] += 1
                await asyncio.sleep(backoff)
                backoff *= 2
            except Exception as e:
                self.circuit_breaker.record_failure()
                if attempt == retries - 1:
                    raise
                telemetry["retry_count"] += 1
                await asyncio.sleep(backoff)
                backoff *= 2
                
        raise ConnectionError("Max retries exceeded")

    async def stream(self, method: str, url: str, headers: Dict[str, str], json: Dict[str, Any] = None) -> AsyncGenerator[Tuple[bytes, Dict[str, float]], None]:
        if not self.circuit_breaker.can_execute():
            raise ConnectionError(f"Circuit Breaker is OPEN for {url}")
            
        telemetry = {
            "start_time": time.time(),
            "first_byte_time": 0.0,
            "total_duration": 0.0,
            "http_status": 200,
            "retry_count": 0
        }
        
        try:
            async with self.client.stream(method, url, headers=headers, json=json) as response:
                telemetry["http_status"] = response.status_code
                response.raise_for_status()
                self.circuit_breaker.record_success()
                
                async for chunk in response.aiter_bytes():
                    if telemetry["first_byte_time"] == 0.0:
                        telemetry["first_byte_time"] = (time.time() - telemetry["start_time"]) * 1000
                    yield chunk, telemetry
                    
            telemetry["total_duration"] = (time.time() - telemetry["start_time"]) * 1000
        except Exception as e:
            self.circuit_breaker.record_failure()
            raise
