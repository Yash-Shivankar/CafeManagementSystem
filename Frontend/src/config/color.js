export const parseTriple = (triple) => {
  const parts = String(triple).trim().split(/[\s,]+/).map(Number);
  if (parts.length !== 3 || parts.some((n) => !Number.isFinite(n) || n < 0 || n > 255)) {
    throw new Error(`Not an "R G B" channel triple: ${JSON.stringify(triple)}`);
  }
  return parts;
};

export const toTriple = ([r, g, b]) =>
  [r, g, b].map((n) => Math.round(Math.min(255, Math.max(0, n)))).join(" ");

export const luminance = (triple) => {
  const [r, g, b] = parseTriple(triple).map((channel) => {
    const c = channel / 255;
    return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
};

export const contrastRatio = (a, b) => {
  const la = luminance(a);
  const lb = luminance(b);
  const [hi, lo] = la > lb ? [la, lb] : [lb, la];
  return (hi + 0.05) / (lo + 0.05);
};

export const WHITE = "255 255 255";
export const BLACK = "0 0 0";

export const onColor = (background, threshold = 4.5) => {
  const soft = "17 24 39";
  const light = contrastRatio(background, WHITE);
  const dark = contrastRatio(background, soft);

  if (light >= dark) {
    return light >= threshold ? WHITE : BLACK;
  }
  return dark >= threshold ? soft : BLACK;
};

export const mix = (a, b, amount) => {
  const [ar, ag, ab] = parseTriple(a);
  const [br, bg, bb] = parseTriple(b);
  const t = Math.min(1, Math.max(0, amount));
  return toTriple([ar + (br - ar) * t, ag + (bg - ag) * t, ab + (bb - ab) * t]);
};

export const modeOf = (background) => (luminance(background) > 0.35 ? "light" : "dark");
