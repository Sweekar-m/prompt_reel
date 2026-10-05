// web/trends/index.js
export async function fetchTrendsAPI() {
  const resp = await fetch('/api/trends');
  return await resp.json();
}
