// web/templates/index.js
export async function fetchStylesAPI() {
  const resp = await fetch('/api/styles');
  return await resp.json();
}
