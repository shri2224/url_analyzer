/**
 * URL Threat Analyzer — Gmail Guard
 * Popup Script
 */

document.addEventListener("DOMContentLoaded", async () => {
    const statusDot = document.getElementById("status-dot");
    const statusText = document.getElementById("status-text");
    const statChecked = document.getElementById("stat-checked");
    const statFlagged = document.getElementById("stat-flagged");
    const backendUrlInput = document.getElementById("backend-url");
    const saveBtn = document.getElementById("save-btn");
    const clearBtn = document.getElementById("clear-btn");

    // Load saved backend URL
    chrome.storage.local.get(["backendUrl"], (result) => {
        backendUrlInput.value = result.backendUrl || "http://127.0.0.1:8000";
    });

    // Load stats
    chrome.runtime.sendMessage({ action: "getStats" }, (stats) => {
        if (stats) {
            statChecked.textContent = stats.checked || 0;
            statFlagged.textContent = stats.flagged || 0;
        }
    });

    // Check backend health
    chrome.runtime.sendMessage({ action: "pingBackend" }, (response) => {
        if (response && response.alive) {
            statusDot.className = "status-dot status-online";
            statusText.textContent = "Backend connected";
            statusText.classList.add("text-online");
        } else {
            statusDot.className = "status-dot status-offline";
            statusText.textContent = "Backend unreachable";
            statusText.classList.add("text-offline");
        }
    });

    // Save backend URL
    saveBtn.addEventListener("click", () => {
        const url = backendUrlInput.value.trim().replace(/\/+$/, "");
        if (url) {
            chrome.storage.local.set({ backendUrl: url }, () => {
                saveBtn.textContent = "✓";
                saveBtn.classList.add("btn-success");
                setTimeout(() => {
                    saveBtn.textContent = "✓";
                    saveBtn.classList.remove("btn-success");
                }, 1500);
                // Re-check health with new URL
                chrome.runtime.sendMessage({ action: "pingBackend" }, (response) => {
                    if (response && response.alive) {
                        statusDot.className = "status-dot status-online";
                        statusText.textContent = "Backend connected";
                        statusText.className = "status-text text-online";
                    } else {
                        statusDot.className = "status-dot status-offline";
                        statusText.textContent = "Backend unreachable";
                        statusText.className = "status-text text-offline";
                    }
                });
            });
        }
    });

    // Clear cache & stats
    clearBtn.addEventListener("click", () => {
        chrome.runtime.sendMessage({ action: "clearCache" }, () => {
            statChecked.textContent = "0";
            statFlagged.textContent = "0";
            clearBtn.textContent = "Cleared ✓";
            setTimeout(() => {
                clearBtn.textContent = "Clear Cache & Stats";
            }, 1500);
        });
    });

    // Enter key saves URL
    backendUrlInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") saveBtn.click();
    });
});
