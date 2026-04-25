/**
 * URL Threat Analyzer — Gmail Guard
 * Content Script — Injected into mail.google.com
 * 
 * Observes DOM for email open events, extracts subject + sender,
 * queries the backend via background.js, and injects warning banners.
 */

(() => {
    "use strict";

    const BANNER_ID = "uta-gmail-guard-banner";
    const CHECK_DEBOUNCE_MS = 800;
    let lastCheckedKey = "";
    let debounceTimer = null;

    // ── Banner HTML builder ───────────────────────────────────────

    function buildBanner(data) {
        const unsafeCount = data.unsafe_count || 0;
        const totalUrls = data.total_urls || 0;
        const verdict = data.overall_verdict || "unsafe";

        const unsafeUrlList = (data.unsafe_urls || [])
            .slice(0, 5) // Show max 5
            .map((u) => {
                const shortUrl = u.url.length > 60 ? u.url.substring(0, 57) + "..." : u.url;
                return `<div class="uta-threat-url">
          <span class="uta-threat-url-icon">🔗</span>
          <span class="uta-threat-url-text" title="${escapeHtml(u.url)}">${escapeHtml(shortUrl)}</span>
          <span class="uta-threat-url-badge">UNSAFE</span>
        </div>`;
            })
            .join("");

        return `
      <div id="${BANNER_ID}" class="uta-banner uta-banner-${verdict}" role="alert">
        <div class="uta-banner-header">
          <div class="uta-banner-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L1 21h22L12 2z" fill="currentColor" opacity="0.2"/>
              <path d="M12 2L1 21h22L12 2z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
              <line x1="12" y1="9" x2="12" y2="14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <circle cx="12" cy="17" r="1" fill="currentColor"/>
            </svg>
          </div>
          <div class="uta-banner-content">
            <div class="uta-banner-title">⚠️ Threat Detected — This email contains malicious URLs</div>
            <div class="uta-banner-subtitle">
              URL Threat Analyzer flagged <strong>${unsafeCount}</strong> of <strong>${totalUrls}</strong> URL${totalUrls !== 1 ? "s" : ""} as unsafe.
              Exercise extreme caution before clicking any links.
            </div>
          </div>
          <button class="uta-banner-close" title="Dismiss warning" aria-label="Dismiss warning">✕</button>
        </div>
        ${unsafeUrlList ? `<div class="uta-banner-details">${unsafeUrlList}</div>` : ""}
        <div class="uta-banner-footer">
          <span class="uta-banner-badge">URL Threat Analyzer</span>
          <a class="uta-banner-link" href="http://localhost:5173" target="_blank" rel="noopener">
            Open Dashboard →
          </a>
        </div>
      </div>
    `;
    }

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }

    // ── Banner injection / removal ────────────────────────────────

    function removeBanner() {
        const existing = document.getElementById(BANNER_ID);
        if (existing) existing.remove();
    }

    function injectBanner(data, container) {
        removeBanner();

        const bannerHtml = buildBanner(data);
        const wrapper = document.createElement("div");
        wrapper.innerHTML = bannerHtml;
        const bannerEl = wrapper.firstElementChild;

        // Insert at top of email view
        container.insertBefore(bannerEl, container.firstChild);

        // Slide-in animation
        requestAnimationFrame(() => {
            bannerEl.classList.add("uta-banner-visible");
        });

        // Close button
        const closeBtn = bannerEl.querySelector(".uta-banner-close");
        if (closeBtn) {
            closeBtn.addEventListener("click", () => {
                bannerEl.classList.remove("uta-banner-visible");
                bannerEl.classList.add("uta-banner-hiding");
                setTimeout(() => bannerEl.remove(), 300);
            });
        }
    }


    // ── Gmail DOM extraction ──────────────────────────────────────

    function getEmailSubject() {
        // Try multiple selectors
        const subjectEl =
            document.querySelector('h2[data-thread-perm-id]') ||
            document.querySelector('h2.hP') ||
            document.querySelector('div[role="main"] h2') ||
            document.querySelector('.ha h2');

        const subject = subjectEl ? subjectEl.textContent.trim() : null;
        if (subject) console.log("[Gmail Guard] Found subject:", subject);
        else console.log("[Gmail Guard] No subject found.");
        return subject;
    }

    function getEmailSender() {
        const senderEl =
            document.querySelector('span[email]') ||
            document.querySelector('span.gD') ||
            document.querySelector('.gE span[email]');

        if (senderEl) {
            const sender = senderEl.getAttribute("email") || senderEl.textContent.trim();
            console.log("[Gmail Guard] Found sender:", sender);
            return sender;
        }
        console.log("[Gmail Guard] No sender found.");
        return null;
    }

    function getEmailContainer() {
        return (
            document.querySelector('div[role="main"] div.nH') ||
            document.querySelector('div[role="main"]') ||
            document.querySelector('div.nH.bkK') ||
            document.querySelector('table.Bs.nH') // fallback
        );
    }

    // ── Check logic ───────────────────────────────────────────────

    async function checkCurrentEmail() {
        const subject = getEmailSubject();
        const sender = getEmailSender();

        if (!subject) {
            console.log("[Gmail Guard] Skipping check: No subject detected.");
            removeBanner();
            return;
        }

        const checkKey = `${subject}|||${sender}`;
        if (checkKey === lastCheckedKey) {
            console.log("[Gmail Guard] Already checked this email, skipping.");
            return;
        }
        lastCheckedKey = checkKey;

        console.log(`[Gmail Guard] Checking email: "${subject}" from "${sender}"...`);

        try {
            const response = await chrome.runtime.sendMessage({
                action: "checkEmail",
                subject,
                sender: sender || ""
            });

            console.log("[Gmail Guard] Backend response:", response);

            if (response && response.found && response.overall_verdict === "unsafe") {
                console.log("[Gmail Guard] Email is UNSAFE. Injecting banner.");
                const container = getEmailContainer();
                if (container) {
                    injectBanner(response, container);
                } else {
                    console.warn("[Gmail Guard] Could not find container to inject banner!");
                }
            } else {
                console.log("[Gmail Guard] Email is SAFE or NOT FOUND.");
                removeBanner();
            }
        } catch (error) {
            console.warn("[Gmail Guard] Check failed:", error);
        }
    }

    function debouncedCheck() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(checkCurrentEmail, CHECK_DEBOUNCE_MS);
    }

    // ── DOM Observer ──────────────────────────────────────────────

    function startObserving() {
        // Watch for Gmail's dynamic content changes
        const observer = new MutationObserver((mutations) => {
            let shouldCheck = false;

            for (const mutation of mutations) {
                // Check for large DOM changes (email being opened)
                if (mutation.addedNodes.length > 0) {
                    for (const node of mutation.addedNodes) {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            // Gmail loads email content into these containers
                            if (
                                node.querySelector?.('h2[data-thread-perm-id]') ||
                                node.querySelector?.('h2.hP') ||
                                node.matches?.('div[role="list"]') ||
                                node.querySelector?.('span[email]') ||
                                node.querySelector?.('div.a3s') // email body container
                            ) {
                                shouldCheck = true;
                                break;
                            }
                        }
                    }
                }
                if (shouldCheck) break;
            }

            if (shouldCheck) {
                debouncedCheck();
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        // Also check on hash change (Gmail uses # navigation)
        window.addEventListener("hashchange", () => {
            lastCheckedKey = ""; // Reset so we re-check
            debouncedCheck();
        });

        // Initial check
        setTimeout(checkCurrentEmail, 2000);
    }

    // ── Init ──────────────────────────────────────────────────────

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", startObserving);
    } else {
        startObserving();
    }

    console.log("[Gmail Guard] Content script loaded on", window.location.hostname);
})();
