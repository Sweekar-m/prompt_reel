import { ColorValue } from "../types";

export function toRgba(color: ColorValue | undefined, alpha: number = 1.0): string {
  if (!color) return `rgba(255, 255, 255, ${alpha})`;
  if (Array.isArray(color)) {
    const [r, g, b] = color;
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }
  if (typeof color === "string") {
    if (color.startsWith("#")) {
      const hex = color.slice(1);
      const r = parseInt(hex.substring(0, 2), 16) || 0;
      const g = parseInt(hex.substring(2, 4), 16) || 0;
      const b = parseInt(hex.substring(4, 6), 16) || 0;
      return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }
    return color;
  }
  return `rgba(255, 255, 255, ${alpha})`;
}

export function toHex(color: ColorValue | undefined): string {
  if (!color) return "#ffffff";
  if (Array.isArray(color)) {
    const [r, g, b] = color;
    return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
  }
  return String(color);
}
