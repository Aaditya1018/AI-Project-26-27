/**
 * SafeStack AI - API Client Service
 */

const API_BASE = '/api';

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}

export async function fetchBays() {
  const res = await fetch(`${API_BASE}/bays`);
  return res.json();
}

export async function fetchEvents(params = {}) {
  const query = new URLSearchParams();
  if (params.bay_id) query.append('bay_id', params.bay_id);
  if (params.risk_tier) query.append('risk_tier', params.risk_tier);
  if (params.status) query.append('status', params.status);
  if (params.limit) query.append('limit', params.limit);

  const res = await fetch(`${API_BASE}/events?${query.toString()}`);
  return res.json();
}

export async function fetchEventDetail(eventId) {
  const res = await fetch(`${API_BASE}/events/${eventId}`);
  return res.json();
}

export async function submitReview(eventId, action, notes, supervisorName = 'Supervisor') {
  const res = await fetch(`${API_BASE}/events/${eventId}/review`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      event_id: eventId,
      action: action,
      notes: notes,
      supervisor_name: supervisorName
    })
  });
  return res.json();
}

export async function fetchEventRCA(eventId) {
  const res = await fetch(`${API_BASE}/events/${eventId}/rca`);
  return res.json();
}

export async function triggerSimulation(bayId, scenarioCode, productCategory) {
  const query = new URLSearchParams({
    bay_id: bayId,
    scenario: scenarioCode,
    product_category: productCategory
  });
  const res = await fetch(`${API_BASE}/simulate/trigger?${query.toString()}`, {
    method: 'POST'
  });
  return res.json();
}

export async function fetchAnalytics() {
  const res = await fetch(`${API_BASE}/analytics/summary`);
  return res.json();
}

export async function sendChatMessage(query, bayId = null) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: query,
      bay_id: bayId
    })
  });
  return res.json();
}

// ----------------- Video Injection APIs -----------------

export async function uploadCustomVideo(file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/video/upload`, {
    method: 'POST',
    body: formData
  });
  return res.json();
}

export async function fetchUploadedVideos() {
  const res = await fetch(`${API_BASE}/video/uploads`);
  return res.json();
}

export async function injectVideoToBay(bayId, filename) {
  const res = await fetch(`${API_BASE}/video/inject`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      bay_id: bayId,
      filename: filename
    })
  });
  return res.json();
}

export async function resetBayVideo(bayId) {
  const res = await fetch(`${API_BASE}/video/reset/${bayId}`, {
    method: 'POST'
  });
  return res.json();
}

export async function processCustomVideoOffline(filename, bayId, category) {
  const res = await fetch(`${API_BASE}/video/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      filename: filename,
      bay_id: bayId,
      product_category: category
    })
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Video scan failed');
  return data;
}
