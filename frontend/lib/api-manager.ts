import axios from "axios";

interface CacheEntry {
  data: any;
  timestamp: number;
}

// In-memory cache for API responses
const apiCache = new Map<string, CacheEntry>();

// Track active promises to deduplicate requests
const activePromises = new Map<string, Promise<any>>();

// Track AbortControllers for active request cancellations
const activeControllers = new Map<string, AbortController>();

interface ApiRequestOptions {
  ttl?: number; // Cache time-to-live in ms (0 to disable cache)
  retries?: number; // Number of retries on failure (default: 2)
  retryDelay?: number; // Delay between retries in ms (default: 500)
  cancelPrevious?: boolean; // Cancel any pending request for the same key (default: true)
}

/**
 * Execute an API request with caching, deduplication, retries, and cancellation support.
 */
export async function executeApiRequest<T>(
  requestFn: (config: { signal?: AbortSignal }) => Promise<T>,
  key: string,
  options: ApiRequestOptions = {}
): Promise<T> {
  const {
    ttl = 10000, // 10 seconds default cache TTL
    retries = 2,
    retryDelay = 500,
    cancelPrevious = true,
  } = options;

  // 1. Cancel previous request for the same key if cancelPrevious is true
  if (cancelPrevious) {
    const oldController = activeControllers.get(key);
    if (oldController) {
      try {
        oldController.abort();
      } catch (err) {
        // Ignore abort errors
      }
      activeControllers.delete(key);
    }
  }

  // Create new AbortController for this request
  const controller = new AbortController();
  activeControllers.set(key, controller);

  // 2. Check if cache contains valid data
  if (ttl > 0) {
    const cached = apiCache.get(key);
    if (cached && Date.now() - cached.timestamp < ttl) {
      return cached.data;
    }
  }

  // 3. Deduplicate requests - if there's already an active promise, return it
  if (activePromises.has(key)) {
    return activePromises.get(key) as Promise<T>;
  }

  // Helper with retry logic
  const runWithRetry = async (attempt: number): Promise<T> => {
    try {
      const result = await requestFn({ signal: controller.signal });
      
      // Store in cache if TTL is set
      if (ttl > 0) {
        apiCache.set(key, { data: result, timestamp: Date.now() });
      }
      
      return result;
    } catch (error: any) {
      // Don't retry if aborted
      if (axios.isCancel(error) || error.name === "AbortError" || controller.signal.aborted) {
        throw error;
      }

      if (attempt < retries) {
        await new Promise((resolve) => setTimeout(resolve, retryDelay * attempt));
        return runWithRetry(attempt + 1);
      }
      throw error;
    }
  };

  const promise = runWithRetry(1).finally(() => {
    activePromises.delete(key);
    if (activeControllers.get(key) === controller) {
      activeControllers.delete(key);
    }
  });

  activePromises.set(key, promise);
  return promise;
}

/**
 * Clear cached entries
 */
export function clearApiCache(keyPrefix?: string) {
  if (keyPrefix) {
    for (const key of apiCache.keys()) {
      if (key.startsWith(keyPrefix)) {
        apiCache.delete(key);
      }
    }
  } else {
    apiCache.clear();
  }
}
