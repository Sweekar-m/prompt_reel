import katex from "katex";

/**
 * Strips outer enclosing dollar signs or markdown backticks from LaTeX strings.
 */
export function cleanLatexString(raw: string): string {
  if (!raw) return "";
  let s = raw.trim();
  // Strip code block backticks
  s = s.replace(/^`+|`+$/g, "").trim();
  // Strip $$ ... $$ or $ ... $
  if (s.startsWith("$$") && s.endsWith("$$") && s.length >= 4) {
    s = s.slice(2, -2).trim();
  } else if (s.startsWith("$") && s.endsWith("$") && s.length >= 2) {
    s = s.slice(1, -1).trim();
  }
  return s;
}

/**
 * Fallback plaintext mathematical cleaner in case KaTeX fails or for plain text display.
 */
export function formatPlainMath(raw: string): string {
  if (!raw) return "";
  let s = cleanLatexString(raw);

  // Vectors
  s = s.replace(/\\vec\s*\{([a-zA-Z0-9]+)\}/g, "$1⃗");
  s = s.replace(/\\vec\s+([a-zA-Z0-9])/g, "$1⃗");

  // Operators and math symbols
  s = s.replace(/\\cdot/g, " · ");
  s = s.replace(/\\times/g, " × ");
  s = s.replace(/\\pm/g, " ± ");
  s = s.replace(/\\neq/g, " ≠ ");
  s = s.replace(/\\approx/g, " ≈ ");
  s = s.replace(/\\leq/g, " ≤ ");
  s = s.replace(/\\geq/g, " ≥ ");
  s = s.replace(/\\infty/g, " ∞ ");
  s = s.replace(/\\partial/g, " ∂");
  s = s.replace(/\\nabla/g, " ∇");

  // Greek letters
  s = s.replace(/\\theta/g, "θ");
  s = s.replace(/\\pi/g, "π");
  s = s.replace(/\\alpha/g, "α");
  s = s.replace(/\\beta/g, "β");
  s = s.replace(/\\gamma/g, "γ");
  s = s.replace(/\\lambda/g, "λ");
  s = s.replace(/\\sigma/g, "σ");
  s = s.replace(/\\omega/g, "ω");
  s = s.replace(/\\phi/g, "ϕ");

  // Trig / functions
  s = s.replace(/\\cos/g, "cos");
  s = s.replace(/\\sin/g, "sin");
  s = s.replace(/\\tan/g, "tan");
  s = s.replace(/\\ln/g, "ln");
  s = s.replace(/\\log/g, "log");
  s = s.replace(/\\exp/g, "exp");

  // Fractions: \frac{a}{b} -> (a / b)
  s = s.replace(/\\frac\s*\{([^}]+)\}\s*\{([^}]+)\}/g, "($1) / ($2)");
  s = s.replace(/\\dfrac\s*\{([^}]+)\}\s*\{([^}]+)\}/g, "($1) / ($2)");

  // Square roots: \sqrt{...} -> √( ... )
  s = s.replace(/\\sqrt\s*\{([^}]+)\}/g, "√($1)");

  // Braces and parens
  s = s.replace(/\\left\s*/g, "");
  s = s.replace(/\\right\s*/g, "");
  s = s.replace(/\\,/g, " ");
  s = s.replace(/\\;/g, " ");
  s = s.replace(/\\!/g, "");

  // Remaining single backslashes
  s = s.replace(/\\/g, "");

  // Super/subscripts
  s = s.replace(/\^2\b/g, "²");
  s = s.replace(/\^3\b/g, "³");

  return s.trim();
}

/**
 * Typesets LaTeX into high-fidelity HTML using KaTeX.
 * Gracefully falls back to formatted unicode mathematical text.
 */
export function renderEquationHtml(raw: string, displayMode: boolean = true): string {
  if (!raw) return "";
  const cleaned = cleanLatexString(raw);

  try {
    return katex.renderToString(cleaned, {
      displayMode,
      throwOnError: false,
      output: "htmlAndMathml",
      strict: false,
    });
  } catch (err) {
    console.warn("[KaTeX] Failed to render LaTeX formula, using clean fallback:", err);
    const plain = formatPlainMath(cleaned);
    return `<span class="math-fallback">${plain}</span>`;
  }
}
