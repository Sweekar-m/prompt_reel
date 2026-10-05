// web/projects/index.js
export async function fetchProjectsAPI() {
  const resp = await fetch('/api/reels');
  return await resp.json();
}
