// src/lib/requestCache.ts
// Simple in-memory request cache and deduplication for API calls
interface RequestCacheEntry<T> {
  promise: Promise<T>;
  timestamp: number;
  result?: T;
}

interface CacheOptions {
  ttl?: number; // Time to live in milliseconds (default: 5 minutes)
  maxConcurrent?: number; // Max concurrent requests for same key (default: 1)
}

class RequestCache {
  private cache = new Map<string, RequestCacheEntry<any>>();
  private defaultTTL = 5 * 60 * 1000; // 5 minutes

  /**
   * Get or create a cached request
   */
  async get<T>(
    key: string, 
    requestFn: () => Promise<T>, 
    options: CacheOptions = {}
  ): Promise<T> {
    const ttl = options.ttl ?? this.defaultTTL;
    // Note: maxConcurrent could be used for rate limiting but not implemented yet
    
    // Check if we have a recent cached result
    const existing = this.cache.get(key);
    if (existing) {
      const age = Date.now() - existing.timestamp;
      
      // If we have a recent result, return it
      if (existing.result && age < ttl) {
        console.log(`[RequestCache] Cache hit for ${key} (age: ${age}ms)`);
        return existing.result;
      }
      
      // If there's an ongoing request, wait for it (deduplication)
      if (age < ttl && existing.promise) {
        console.log(`[RequestCache] Deduplicating request for ${key}`);
        try {
          return await existing.promise;
        } catch (error) {
          // If the ongoing request fails, remove it from cache and try again
          this.cache.delete(key);
        }
      }
      
      // Cache entry is stale, remove it
      this.cache.delete(key);
    }

    // Create new request
    console.log(`[RequestCache] Making new request for ${key}`);
    const promise = requestFn();
    
    // Store the promise immediately for deduplication
    const entry: RequestCacheEntry<T> = {
      promise,
      timestamp: Date.now()
    };
    this.cache.set(key, entry);

    try {
      const result = await promise;
      // Update the cache entry with the result
      entry.result = result;
      return result;
    } catch (error) {
      // Remove failed request from cache
      this.cache.delete(key);
      throw error;
    }
  }

  /**
   * Invalidate cache entries by key pattern
   */
  invalidate(keyPattern: string | RegExp): void {
    const keys = Array.from(this.cache.keys());
    const keysToDelete = keys.filter(key => {
      if (typeof keyPattern === 'string') {
        return key.includes(keyPattern);
      } else {
        return keyPattern.test(key);
      }
    });
    
    keysToDelete.forEach(key => {
      console.log(`[RequestCache] Invalidating ${key}`);
      this.cache.delete(key);
    });
  }

  /**
   * Clear all cache entries
   */
  clear(): void {
    console.log('[RequestCache] Clearing all cache entries');
    this.cache.clear();
  }

  /**
   * Get cache statistics
   */
  getStats() {
    return {
      size: this.cache.size,
      entries: Array.from(this.cache.keys())
    };
  }
}

// Global instance
export const requestCache = new RequestCache();