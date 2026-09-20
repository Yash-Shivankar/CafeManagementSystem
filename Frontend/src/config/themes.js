import { contrastRatio, mix, modeOf, onColor, WHITE, BLACK } from "./color";

export const themes = {
  mysticForest: {
    "--color-primary": "34 197 94",
    "--color-primary-dark": "21 128 61",
    "--color-primary-light": "74 222 128",
    "--color-secondary": "16 185 129",
    "--color-secondary-dark": "15 118 110",
    "--color-secondary-light": "52 211 153",
    "--color-accent": "45 212 191",
    "--color-success": "34 197 94",
    "--color-warning": "245 158 11",
    "--color-error": "220 38 38",
    "--color-info": "14 165 233",
    "--color-background": "19 35 23",
    "--color-surface": "25 53 35",
    "--color-text-primary": "229 245 224",
    "--color-text-secondary": "167 215 169",
    "--color-border": "20 83 45",
  },
  twilight: {
    "--color-primary": "147 51 234",
    "--color-primary-dark": "126 34 206",
    "--color-primary-light": "168 85 247",
    "--color-secondary": "79 70 229",
    "--color-secondary-dark": "55 48 163",
    "--color-secondary-light": "129 140 248",
    "--color-accent": "99 102 241",
    "--color-success": "16 185 129",
    "--color-warning": "245 158 11",
    "--color-error": "239 68 68",
    "--color-info": "59 130 246",
    "--color-background": "36 25 55",
    "--color-surface": "54 37 55",
    "--color-text-primary": "237 233 254",
    "--color-text-secondary": "196 181 253",
    "--color-border": "76 29 149",
  },
  dragonFire: {
    "--color-primary": "220 38 38",
    "--color-primary-dark": "153 27 27",
    "--color-primary-light": "248 113 113",
    "--color-secondary": "251 146 60",
    "--color-secondary-dark": "234 88 12",
    "--color-secondary-light": "253 186 116",
    "--color-accent": "249 115 22",
    "--color-success": "34 197 94",
    "--color-warning": "245 158 11",
    "--color-error": "220 38 38",
    "--color-info": "249 115 22",
    "--color-background": "45 7 7",
    "--color-surface": "69 7 7",
    "--color-text-primary": "255 241 230",
    "--color-text-secondary": "254 202 202",
    "--color-border": "127 29 29",
  },
  oceanDream: {
    "--color-primary": "14 165 233",
    "--color-primary-dark": "3 105 161",
    "--color-primary-light": "56 189 248",
    "--color-secondary": "6 182 212",
    "--color-secondary-dark": "14 116 144",
    "--color-secondary-light": "103 232 249",
    "--color-accent": "8 145 178",
    "--color-success": "16 185 129",
    "--color-warning": "245 158 11",
    "--color-error": "239 68 68",
    "--color-info": "59 130 246",
    "--color-background": "12 44 64",
    "--color-surface": "18 52 76",
    "--color-text-primary": "224 242 254",
    "--color-text-secondary": "186 230 253",
    "--color-border": "22 78 99",
  },
  starlight: {
    "--color-primary": "253 224 71",
    "--color-primary-dark": "202 138 4",
    "--color-primary-light": "254 240 138",
    "--color-secondary": "129 140 248",
    "--color-secondary-dark": "79 70 229",
    "--color-secondary-light": "165 180 252",
    "--color-accent": "99 102 241",
    "--color-success": "16 185 129",
    "--color-warning": "245 158 11",
    "--color-error": "239 68 68",
    "--color-info": "59 130 246",
    "--color-background": "17 24 39",
    "--color-surface": "31 41 55",
    "--color-text-primary": "243 244 246",
    "--color-text-secondary": "209 213 219",
    "--color-border": "55 65 81",
  },
  sunriseBlush: {
    "--color-primary": "244 114 182",
    "--color-primary-dark": "190 24 93",
    "--color-primary-light": "249 168 212",
    "--color-secondary": "251 191 36",
    "--color-secondary-dark": "180 83 9",
    "--color-secondary-light": "252 211 77",
    "--color-accent": "245 158 11",
    "--color-success": "16 185 129",
    "--color-warning": "249 115 22",
    "--color-error": "220 38 38",
    "--color-info": "59 130 246",
    "--color-background": "255 247 237",
    "--color-surface": "255 228 230",
    "--color-text-primary": "31 41 55",
    "--color-text-secondary": "107 114 128",
    "--color-border": "251 207 232",
  },
  frostVale: {
    "--color-primary": "96 165 250",
    "--color-primary-dark": "29 78 216",
    "--color-primary-light": "147 197 253",
    "--color-secondary": "167 139 250",
    "--color-secondary-dark": "109 40 217",
    "--color-secondary-light": "196 181 253",
    "--color-accent": "99 102 241",
    "--color-success": "34 197 94",
    "--color-warning": "245 158 11",
    "--color-error": "239 68 68",
    "--color-info": "14 165 233",
    "--color-background": "240 249 255",
    "--color-surface": "224 242 254",
    "--color-text-primary": "30 58 138",
    "--color-text-secondary": "59 130 246",
    "--color-border": "191 219 254",
  },
  emberGlow: {
    "--color-primary": "249 115 22",
    "--color-primary-dark": "194 65 12",
    "--color-primary-light": "253 186 116",
    "--color-secondary": "220 38 38",
    "--color-secondary-dark": "153 27 27",
    "--color-secondary-light": "248 113 113",
    "--color-accent": "251 146 60",
    "--color-success": "34 197 94",
    "--color-warning": "245 158 11",
    "--color-error": "220 38 38",
    "--color-info": "249 115 22",
    "--color-background": "28 25 23",
    "--color-surface": "41 37 36",
    "--color-text-primary": "245 245 244",
    "--color-text-secondary": "214 211 209",
    "--color-border": "68 64 60",
  },
};

export const themeLabels = {
  mysticForest: "Forest (dark)",
  twilight: "Twilight (dark)",
  dragonFire: "Crimson (dark)",
  oceanDream: "Ocean (dark)",
  starlight: "Midnight (dark)",
  emberGlow: "Ember (dark)",
  sunriseBlush: "Blush (light)",
  frostVale: "Frost (light)",
};

export const deriveTokens = (palette) => {
  const background = palette["--color-background"];
  const surface = palette["--color-surface"];
  const foreground = palette["--color-text-primary"];
  const mode = modeOf(background);

  const muted = mix(surface, foreground, 0.08);

  return {
    ...palette,
    "--color-foreground": foreground,
    "--color-muted": muted,
    "--color-muted-foreground": palette["--color-text-secondary"],
    "--color-on-primary": onColor(palette["--color-primary"]),
    "--color-on-secondary": onColor(palette["--color-secondary"]),
    "--color-on-accent": onColor(palette["--color-accent"]),
    "--color-on-success": onColor(palette["--color-success"]),
    "--color-on-warning": onColor(palette["--color-warning"]),
    "--color-on-error": onColor(palette["--color-error"]),
    "--color-on-info": onColor(palette["--color-info"]),
    "--color-scrim": mode === "light" ? "17 24 39" : BLACK,
    "--scrim-opacity": mode === "light" ? "0.35" : "0.55",
    "--color-sheen": mode === "light" ? BLACK : WHITE,
    "--sheen-opacity": mode === "light" ? "0.04" : "0.10",
    "--color-star": palette["--color-warning"],
    "--color-star-empty": mix(background, foreground, 0.28),
    "--theme-mode": mode,
  };
};

export const applyTheme = (theme) => {
  const palette = typeof theme === "string" ? themes[theme] : theme;

  if (!palette || typeof palette !== "object") {
    console.warn("Invalid theme passed to applyTheme:", theme);
    return;
  }

  const tokens = deriveTokens(palette);
  const root = document.documentElement;

  Object.entries(tokens).forEach(([key, value]) => {
    root.style.setProperty(key, value);
  });

  root.style.colorScheme = tokens["--theme-mode"];
  root.dataset.themeMode = tokens["--theme-mode"];
};

export const onColorContrast = (palette, token) =>
  contrastRatio(palette[`--color-${token}`], deriveTokens(palette)[`--color-on-${token}`]);
