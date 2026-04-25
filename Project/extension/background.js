/**
 * URL Threat Analyzer — Gmail Guard
 * Background Service Worker
 * 
 * Bridges content script ↔ backend API with caching.
 */

const DEFAULT_BACKEND = "http://127.0.0.1:8000";
const CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes

// In-memory cache (service worker lifetime)
const cache = new Map();

/**
 * Get the configured backend URL from storage.
 */
async function getBackendUrl() {
    return new Promise((resolve) => {
        chrome.storage.local.get(["backendUrl"], (result) => {
            resolve(result.backendUrl || DEFAULT_BACKEND);
        });
    });
}

/**
 * Check a specific email against the backend scan results.
 */
async function checkEmail(subject, sender) {
    const cacheKey = `${subject}|||${sender}`.toLowerCase();

    // Check cache
    const cached = cache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < CACHE_TTL_MS) {
        return cached.data;
    }

    const backendUrl = await getBackendUrl();
    const params = new URLSearchParams({ subject, sender });
    const url = `${backendUrl}/api/gmail/check-email?${params.toString()}`;

    try {
        const response = await fetch(url, {
            method: "GET",
            headers: { "Accept": "application/json" }
        });

        if (!response.ok) {
            throw new Error(`Backend returned ${response.status}`);
        }

        const data = await response.json();

        // Cache the result
        cache.set(cacheKey, { data, timestamp: Date.now() });

        // Update stats
        updateStats(data);

        return data;
    } catch (error) {
        console.error("[Gmail Guard] Backend check failed:", error.message);
        return { found: false, overall_verdict: "error", error: error.message };
    }
}

/**
 * Update extension badge and stored stats.
 */
async function updateStats(data) {
    chrome.storage.local.get(["stats"], (result) => {
        const stats = result.stats || { checked: 0, flagged: 0 };
        stats.checked++;
        if (data.found && data.overall_verdict === "unsafe") {
            stats.flagged++;
        }
        chrome.storage.local.set({ stats });
    });
}

/**
 * Ping backend health endpoint.
 */
async function pingBackend() {
    const backendUrl = await getBackendUrl();
    try {
        const response = await fetch(`${backendUrl}/api/ping`, {
            method: "GET",
            signal: AbortSignal.timeout(5000)
        });
        return response.ok;
    } catch {
        return false;
    }
}

// ── Message listener ──────────────────────────────────────────────

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "checkEmail") {
        checkEmail(message.subject || "", message.sender || "")
            .then(sendResponse)
            .catch((err) => sendResponse({ found: false, error: err.message }));
        return true; // Keep message channel open for async response
    }

    if (message.action === "pingBackend") {
        pingBackend()
            .then((alive) => sendResponse({ alive }))
            .catch(() => sendResponse({ alive: false }));
        return true;
    }

    if (message.action === "getStats") {
        chrome.storage.local.get(["stats"], (result) => {
            sendResponse(result.stats || { checked: 0, flagged: 0 });
        });
        return true;
    }

    if (message.action === "clearCache") {
        cache.clear();
        chrome.storage.local.set({ stats: { checked: 0, flagged: 0 } });
        sendResponse({ success: true });
        return true;
    }
});

// Set badge on install
chrome.runtime.onInstalled.addListener(() => {
    chrome.storage.local.set({
        backendUrl: DEFAULT_BACKEND,
        stats: { checked: 0, flagged: 0 }
    });
    console.log("[Gmail Guard] Extension installed. Backend:", DEFAULT_BACKEND);
});


// ── Heartbeat Logic ──────────────────────────────────────────

async function sendHeartbeat() {
    try {
        const backendUrl = await getBackendUrl();
        await fetch(`${backendUrl}/api/extension/heartbeat`, {
            method: 'POST'
        });
        console.log("[Gmail Guard] Heartbeat sent.");
    } catch (error) {
        console.warn("[Gmail Guard] Heartbeat failed:", error);
    }
}

// Send heartbeat on startup
sendHeartbeat();

// Send heartbeat every 5 minutes
setInterval(sendHeartbeat, 5 * 60 * 1000);

