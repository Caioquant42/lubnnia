# Crypto Collar Caching Implementation Plan

## Overview

This document outlines the implementation plan for adding server-side caching to the crypto collar endpoint (`/api/crypto-collar`). Currently, the endpoint calculates all strategies in real-time by fetching data from the Bybit API on every request, which can be slow and expensive.

## Current State

### How It Works Now
- **Real-time calculation**: Every request triggers:
  1. API calls to Bybit to fetch options instruments
  2. API calls to Bybit to fetch ticker data (prices, Greeks)
  3. API call to Bybit to fetch spot price
  4. Calculation of all collar combinations
  5. Calculation of strategy metrics (gain, risk, ratios)
  6. Organization by protection type and maturity

- **Performance**: 
  - Slow response times (2-5 seconds per request)
  - High API rate limit usage
  - No caching mechanism

- **HTTP Cache**: Only browser-level caching via `Cache-Control: public, max-age=300` (5 minutes)

## Caching Strategy Options

### Option 1: Redis Caching (Recommended for Production)

**Pros:**
- Shared across multiple server instances
- Persistent across server restarts (if configured)
- Better for distributed systems
- Can be monitored and managed separately

**Cons:**
- Requires Redis server running
- Additional dependency
- Slightly more complex setup

### Option 2: In-Memory Caching (Simpler, Good for Single Instance)

**Pros:**
- No additional dependencies
- Faster than Redis (no network overhead)
- Simple implementation
- Already used in `CollarResource` class

**Cons:**
- Lost on server restart
- Not shared across instances
- Limited by server memory

## Recommended Implementation: Hybrid Approach

Start with **in-memory caching** (quick win), then migrate to **Redis** if needed for production scaling.

---

## Implementation Plan: In-Memory Caching

### Step 1: Create Cache Utility Module

**File**: `backend/app/utils/cache_utils.py`

```python
"""
Cache utilities for crypto collar strategies
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib
import json

class CryptoCollarCache:
    """
    In-memory cache for crypto collar strategies
    """
    _cache: Dict[str, Dict[str, Any]] = {}
    
    @staticmethod
    def _generate_cache_key(
        underlying: str,
        exchange: str,
        min_days: int,
        max_days: int,
        min_gain_to_risk: float
    ) -> str:
        """
        Generate a unique cache key from parameters
        """
        key_string = f"{underlying}:{exchange}:{min_days}:{max_days}:{min_gain_to_risk}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    @staticmethod
    def get(
        underlying: str,
        exchange: str,
        min_days: int,
        max_days: int,
        min_gain_to_risk: float,
        cache_ttl: int = 300  # 5 minutes default
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached data if available and not expired
        """
        cache_key = CryptoCollarCache._generate_cache_key(
            underlying, exchange, min_days, max_days, min_gain_to_risk
        )
        
        if cache_key not in CryptoCollarCache._cache:
            return None
        
        cached_data = CryptoCollarCache._cache[cache_key]
        cached_time = datetime.fromisoformat(cached_data['timestamp'])
        
        # Check if cache is expired
        if datetime.now() - cached_time > timedelta(seconds=cache_ttl):
            del CryptoCollarCache._cache[cache_key]
            return None
        
        return cached_data['data']
    
    @staticmethod
    def set(
        underlying: str,
        exchange: str,
        min_days: int,
        max_days: int,
        min_gain_to_risk: float,
        data: Dict[str, Any]
    ) -> None:
        """
        Store data in cache
        """
        cache_key = CryptoCollarCache._generate_cache_key(
            underlying, exchange, min_days, max_days, min_gain_to_risk
        )
        
        CryptoCollarCache._cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def clear() -> None:
        """
        Clear all cached data (useful for testing or manual invalidation)
        """
        CryptoCollarCache._cache.clear()
    
    @staticmethod
    def clear_for_underlying(underlying: str) -> None:
        """
        Clear cache for a specific underlying asset
        """
        keys_to_delete = []
        for key, value in CryptoCollarCache._cache.items():
            if value['data'].get('metadata', {}).get('underlying') == underlying:
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del CryptoCollarCache._cache[key]
    
    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """
        Get cache statistics
        """
        return {
            'total_entries': len(CryptoCollarCache._cache),
            'cache_keys': list(CryptoCollarCache._cache.keys())
        }
```

### Step 2: Update CryptoCollarResource

**File**: `backend/app/api/routes.py`

**Changes needed:**

1. Import the cache utility:
```python
from ..utils.cache_utils import CryptoCollarCache
```

2. Modify the `get` method to use caching:

```python
class CryptoCollarResource(Resource):
    """
    API endpoint for crypto collar strategies
    """
    def get(self):
        try:
            # Get query parameters
            underlying = request.args.get('underlying', 'BTC')
            exchange = request.args.get('exchange', 'bybit')
            min_days = request.args.get('min_days', 0, type=int)
            max_days = request.args.get('max_days', 90, type=int)
            min_gain_to_risk = request.args.get('min_gain_to_risk', 0.0, type=float)
            
            # Check cache first
            cached_data = CryptoCollarCache.get(
                underlying=underlying,
                exchange=exchange,
                min_days=min_days,
                max_days=max_days,
                min_gain_to_risk=min_gain_to_risk,
                cache_ttl=300  # 5 minutes
            )
            
            if cached_data:
                current_app.logger.info(
                    f"Cache HIT for crypto collar: {underlying} on {exchange}"
                )
                response = make_response(jsonify(cached_data))
                response.headers['Cache-Control'] = 'public, max-age=300'
                response.headers['X-Cache-Status'] = 'HIT'
                return response
            
            # Cache miss - fetch and calculate
            current_app.logger.info(
                f"Cache MISS - Fetching crypto collar for {underlying} on {exchange}"
            )
            
            # Get collar analysis
            collar_data = get_crypto_collar_analysis(
                underlying=underlying,
                exchange=exchange,
                min_days=min_days,
                max_days=max_days,
                min_gain_to_risk=min_gain_to_risk
            )
            
            current_app.logger.info(
                f"Crypto collar data retrieved: {collar_data['metadata']['total_count']} strategies"
            )
            
            # Store in cache
            CryptoCollarCache.set(
                underlying=underlying,
                exchange=exchange,
                min_days=min_days,
                max_days=max_days,
                min_gain_to_risk=min_gain_to_risk,
                data=collar_data
            )
            
            response = make_response(jsonify(collar_data))
            response.headers['Cache-Control'] = 'public, max-age=300'
            response.headers['X-Cache-Status'] = 'MISS'
            return response
            
        except Exception as e:
            current_app.logger.error(f"Error in CryptoCollarResource: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            return {'error': str(e)}, 500
```

### Step 3: Add Cache Management Endpoint (Optional)

**File**: `backend/app/api/routes.py`

Add a new resource for cache management:

```python
class CryptoCollarCacheResource(Resource):
    """
    Cache management endpoint for crypto collar
    """
    def delete(self):
        """
        Clear cache - DELETE /api/crypto-collar/cache
        Query params:
            - underlying: Clear cache for specific underlying (optional)
        """
        try:
            underlying = request.args.get('underlying')
            
            if underlying:
                CryptoCollarCache.clear_for_underlying(underlying)
                return make_response(jsonify({
                    'message': f'Cache cleared for {underlying}',
                    'underlying': underlying
                }), 200)
            else:
                CryptoCollarCache.clear()
                return make_response(jsonify({
                    'message': 'All crypto collar cache cleared'
                }), 200)
                
        except Exception as e:
            current_app.logger.error(f"Error clearing cache: {str(e)}")
            return {'error': str(e)}, 500
    
    def get(self):
        """
        Get cache statistics - GET /api/crypto-collar/cache
        """
        try:
            stats = CryptoCollarCache.get_stats()
            return make_response(jsonify(stats), 200)
        except Exception as e:
            current_app.logger.error(f"Error getting cache stats: {str(e)}")
            return {'error': str(e)}, 500
```

**File**: `backend/app/api/__init__.py`

Register the cache management endpoint:

```python
api.add_resource(CryptoCollarCacheResource, '/crypto-collar/cache')
```

---

## Implementation Plan: Redis Caching (Advanced)

### Prerequisites

1. Redis server running (already configured for Celery)
2. Install Redis Python client: `pip install redis`

### Step 1: Create Redis Cache Utility

**File**: `backend/app/utils/redis_cache_utils.py`

```python
"""
Redis cache utilities for crypto collar strategies
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib
import json
import redis
from flask import current_app

class RedisCryptoCollarCache:
    """
    Redis-based cache for crypto collar strategies
    """
    def __init__(self):
        # Use existing Redis connection from Celery config
        redis_url = current_app.config.get('broker_url', 'redis://localhost:6379/0')
        # Parse Redis URL and connect
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.cache_prefix = 'crypto_collar:'
        self.default_ttl = 300  # 5 minutes
    
    def _generate_cache_key(
        self,
        underlying: str,
        exchange: str,
        min_days: int,
        max_days: int,
        min_gain_to_risk: float
    ) -> str:
        """
        Generate a unique cache key from parameters
        """
        key_string = f"{underlying}:{exchange}:{min_days}:{max_days}:{min_gain_to_risk}"
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"{self.cache_prefix}{key_hash}"
    
    def get(
        self,
        underlying: str,
        exchange: str,
        min_days: int,
        max_days: int,
        min_gain_to_risk: float
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached data from Redis
        """
        try:
            cache_key = self._generate_cache_key(
                underlying, exchange, min_days, max_days, min_gain_to_risk
            )
            
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            current_app.logger.error(f"Redis cache get error: {str(e)}")
            return None
    
    def set(
        self,
        underlying: str,
        exchange: str,
        min_days: int,
        max_days: int,
        min_gain_to_risk: float,
        data: Dict[str, Any],
        ttl: int = None
    ) -> None:
        """
        Store data in Redis cache
        """
        try:
            cache_key = self._generate_cache_key(
                underlying, exchange, min_days, max_days, min_gain_to_risk
            )
            
            ttl = ttl or self.default_ttl
            self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(data)
            )
        except Exception as e:
            current_app.logger.error(f"Redis cache set error: {str(e)}")
    
    def clear(self) -> None:
        """
        Clear all crypto collar cache entries
        """
        try:
            pattern = f"{self.cache_prefix}*"
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            current_app.logger.error(f"Redis cache clear error: {str(e)}")
    
    def clear_for_underlying(self, underlying: str) -> None:
        """
        Clear cache for a specific underlying asset
        Note: This requires scanning all keys, which can be slow
        For better performance, consider using Redis sets to track keys per underlying
        """
        try:
            pattern = f"{self.cache_prefix}*"
            keys = self.redis_client.keys(pattern)
            
            for key in keys:
                cached_data = self.redis_client.get(key)
                if cached_data:
                    data = json.loads(cached_data)
                    if data.get('metadata', {}).get('underlying') == underlying:
                        self.redis_client.delete(key)
        except Exception as e:
            current_app.logger.error(f"Redis cache clear for underlying error: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        """
        try:
            pattern = f"{self.cache_prefix}*"
            keys = self.redis_client.keys(pattern)
            return {
                'total_entries': len(keys),
                'cache_prefix': self.cache_prefix
            }
        except Exception as e:
            current_app.logger.error(f"Redis cache stats error: {str(e)}")
            return {'error': str(e)}
```

### Step 2: Update CryptoCollarResource for Redis

**File**: `backend/app/api/routes.py`

```python
from ..utils.redis_cache_utils import RedisCryptoCollarCache

class CryptoCollarResource(Resource):
    def __init__(self):
        self.cache = RedisCryptoCollarCache()
    
    def get(self):
        # Same implementation as in-memory, but using self.cache instead
        # ...
```

---

## Configuration Options

### Environment Variables

Add to `backend/.env`:

```env
# Crypto Collar Cache Configuration
CRYPTO_COLLAR_CACHE_TTL=300  # Cache TTL in seconds (default: 5 minutes)
CRYPTO_COLLAR_CACHE_ENABLED=true  # Enable/disable caching
CRYPTO_COLLAR_USE_REDIS=false  # Use Redis instead of in-memory (default: false)
```

### Update Config Class

**File**: `backend/config.py`

```python
class Config:
    # ... existing config ...
    
    # Crypto Collar Cache Settings
    CRYPTO_COLLAR_CACHE_TTL = int(os.environ.get('CRYPTO_COLLAR_CACHE_TTL', 300))
    CRYPTO_COLLAR_CACHE_ENABLED = os.environ.get('CRYPTO_COLLAR_CACHE_ENABLED', 'true').lower() == 'true'
    CRYPTO_COLLAR_USE_REDIS = os.environ.get('CRYPTO_COLLAR_USE_REDIS', 'false').lower() == 'true'
```

---

## Cache Invalidation Strategies

### 1. Time-Based Expiration (TTL)
- **Default**: 5 minutes (300 seconds)
- **Rationale**: Crypto prices change frequently, but options data is relatively stable
- **Configurable**: Via environment variable

### 2. Manual Invalidation
- **Endpoint**: `DELETE /api/crypto-collar/cache?underlying=BTC`
- **Use case**: After major market events or data updates

### 3. Automatic Invalidation on Errors
- If Bybit API fails, don't cache the error
- Log cache misses for monitoring

### 4. Smart Invalidation (Future Enhancement)
- Monitor spot price changes
- Invalidate cache if spot price moves >5% from cached value
- Use Redis pub/sub for distributed cache invalidation

---

## Testing Plan

### 1. Unit Tests

**File**: `backend/tests/test_crypto_collar_cache.py`

```python
import unittest
from app.utils.cache_utils import CryptoCollarCache

class TestCryptoCollarCache(unittest.TestCase):
    def setUp(self):
        CryptoCollarCache.clear()
    
    def test_cache_set_and_get(self):
        test_data = {'metadata': {'underlying': 'BTC'}}
        CryptoCollarCache.set('BTC', 'bybit', 0, 90, 0.0, test_data)
        cached = CryptoCollarCache.get('BTC', 'bybit', 0, 90, 0.0)
        self.assertEqual(cached, test_data)
    
    def test_cache_expiration(self):
        test_data = {'metadata': {'underlying': 'BTC'}}
        CryptoCollarCache.set('BTC', 'bybit', 0, 90, 0.0, test_data)
        # Simulate expiration by using very short TTL
        cached = CryptoCollarCache.get('BTC', 'bybit', 0, 90, 0.0, cache_ttl=0)
        self.assertIsNone(cached)
    
    def test_cache_clear(self):
        test_data = {'metadata': {'underlying': 'BTC'}}
        CryptoCollarCache.set('BTC', 'bybit', 0, 90, 0.0, test_data)
        CryptoCollarCache.clear()
        cached = CryptoCollarCache.get('BTC', 'bybit', 0, 90, 0.0)
        self.assertIsNone(cached)
```

### 2. Integration Tests

Test the full endpoint with caching:

```python
def test_crypto_collar_endpoint_caching(client):
    # First request - should be cache MISS
    response1 = client.get('/api/crypto-collar?underlying=BTC')
    assert response1.status_code == 200
    assert response1.headers.get('X-Cache-Status') == 'MISS'
    
    # Second request - should be cache HIT
    response2 = client.get('/api/crypto-collar?underlying=BTC')
    assert response2.status_code == 200
    assert response2.headers.get('X-Cache-Status') == 'HIT'
    
    # Verify data is the same
    assert response1.json == response2.json
```

### 3. Performance Tests

Measure improvement:

```python
import time

def test_performance_improvement(client):
    # First request (cache miss)
    start = time.time()
    response1 = client.get('/api/crypto-collar?underlying=BTC')
    miss_time = time.time() - start
    
    # Second request (cache hit)
    start = time.time()
    response2 = client.get('/api/crypto-collar?underlying=BTC')
    hit_time = time.time() - start
    
    # Cache hit should be at least 10x faster
    assert hit_time < miss_time / 10
    print(f"Cache miss: {miss_time:.2f}s, Cache hit: {hit_time:.2f}s")
```

---

## Monitoring and Observability

### 1. Logging

Add cache metrics to logs:

```python
current_app.logger.info(
    f"Crypto collar cache: HIT={cache_hits}, MISS={cache_misses}, "
    f"HIT_RATE={hit_rate:.2%}"
)
```

### 2. Response Headers

Already implemented:
- `X-Cache-Status`: 'HIT' or 'MISS'
- `Cache-Control`: Browser cache directive

### 3. Metrics Endpoint

Add to cache management endpoint:
- Total cache entries
- Cache hit rate
- Average response times
- Memory usage (for in-memory cache)

---

## Migration Path

### Phase 1: In-Memory Caching (Week 1)
1. ✅ Create `cache_utils.py`
2. ✅ Update `CryptoCollarResource`
3. ✅ Add cache management endpoint
4. ✅ Deploy and monitor

### Phase 2: Optimization (Week 2-3)
1. Monitor cache hit rates
2. Adjust TTL based on usage patterns
3. Add cache statistics dashboard
4. Optimize cache key generation

### Phase 3: Redis Migration (If Needed)
1. Implement Redis cache utility
2. Add feature flag for Redis vs in-memory
3. A/B test performance
4. Migrate if benefits are clear

---

## Expected Performance Improvements

### Before Caching
- **Response time**: 2-5 seconds
- **API calls per request**: 3+ (instruments, tickers, spot)
- **Rate limit usage**: High
- **Server load**: High (CPU for calculations)

### After Caching (5-minute TTL)
- **Response time (cache hit)**: <50ms
- **API calls per request (cache hit)**: 0
- **Rate limit usage**: Reduced by ~95% (assuming 5-minute cache)
- **Server load**: Minimal for cached requests

### Cache Hit Rate Expectations
- **High traffic**: 80-95% hit rate
- **Low traffic**: 50-70% hit rate
- **First request**: Always cache miss (expected)

---

## Rollback Plan

If issues occur:

1. **Disable caching**: Set `CRYPTO_COLLAR_CACHE_ENABLED=false`
2. **Clear cache**: `DELETE /api/crypto-collar/cache`
3. **Revert code**: Git revert to previous version
4. **Monitor**: Check error logs and response times

---

## Additional Considerations

### 1. Cache Warming
Consider pre-populating cache for popular underlyings:
- BTC, ETH, SOL
- Run background job every 5 minutes

### 2. Cache Compression
For large responses, consider compressing cached data:
- Use `gzip` or `lz4` compression
- Trade-off: CPU vs memory

### 3. Distributed Caching
If using multiple server instances:
- Use Redis (not in-memory)
- Consider cache coherency strategies

### 4. Cache Versioning
Add version to cache keys:
- Invalidate all caches on code changes
- Use semantic versioning

---

## Summary

This implementation plan provides:

1. ✅ **Quick win**: In-memory caching (simple, fast)
2. ✅ **Scalability path**: Redis option for production
3. ✅ **Monitoring**: Cache statistics and logging
4. ✅ **Flexibility**: Configurable TTL and enable/disable
5. ✅ **Safety**: Easy rollback and error handling

**Recommended next steps:**
1. Implement in-memory caching first
2. Deploy and monitor for 1-2 weeks
3. Evaluate performance
4. Consider Redis migration if needed

---

## Files to Create/Modify

### New Files
- `backend/app/utils/cache_utils.py` - In-memory cache utility
- `backend/app/utils/redis_cache_utils.py` - Redis cache utility (optional)
- `backend/tests/test_crypto_collar_cache.py` - Unit tests

### Modified Files
- `backend/app/api/routes.py` - Update `CryptoCollarResource` and add `CryptoCollarCacheResource`
- `backend/app/api/__init__.py` - Register cache management endpoint
- `backend/config.py` - Add cache configuration options
- `backend/.env` - Add cache environment variables

### Documentation
- `docs/CRYPTO_COLLAR_CACHING.md` - This file

---

## Questions or Issues?

If you encounter any issues during implementation:
1. Check logs for cache-related errors
2. Verify Redis is running (if using Redis option)
3. Test cache manually using the cache management endpoint
4. Monitor cache hit rates and adjust TTL if needed

