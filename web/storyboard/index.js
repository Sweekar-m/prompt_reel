// web/storyboard/index.js
export async function getStoryboardAPI(reelId) {
  const resp = await fetch(`/api/reels/${reelId}`);
  return await resp.json();
}
