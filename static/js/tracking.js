function trackDOE(eventName) {
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({
    event: eventName,
    page: window.location.pathname,
    source: document.referrer || "direct"
  });

  fetch("/track", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      event_name: eventName,
      page: window.location.pathname,
      source: document.referrer || "direct"
    })
  }).catch(() => {});
}
