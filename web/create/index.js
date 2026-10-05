// web/create/index.js
export async function createReelAPI(topic, style, duration = 50.0) {
  const resp = await fetch('/api/reels', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic, style, duration })
  });
  return await resp.json();
}
