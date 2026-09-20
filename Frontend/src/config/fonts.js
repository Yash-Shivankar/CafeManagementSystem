export const SYSTEM_FONTS = {
  System:
    'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  Arial: "Arial, Helvetica, sans-serif",
  Georgia: 'Georgia, "Times New Roman", serif',
  TimesNewRoman: '"Times New Roman", Times, serif',
};

export const WEB_FONTS = {
  Inter:
    'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
  Roboto:
    'Roboto, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
  Poppins:
    'Poppins, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
  Lato: 'Lato, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
  PlayfairDisplay: '"Playfair Display", Georgia, "Times New Roman", serif',
  Merriweather: 'Merriweather, Georgia, "Times New Roman", serif',
  CormorantGaramond: '"Cormorant Garamond", Georgia, serif',
  Cinzel: 'Cinzel, Georgia, "Times New Roman", serif',
  CinzelDecorative: '"Cinzel Decorative", Georgia, "Times New Roman", serif',
  YesevaOne: '"Yeseva One", Georgia, serif',
  AbrilFatface: '"Abril Fatface", Georgia, serif',
  Raleway:
    'Raleway, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
  Montserrat:
    'Montserrat, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
  Orbitron: "Orbitron, system-ui, sans-serif",
  DancingScript: '"Dancing Script", "Brush Script MT", cursive',
  Pacifico: 'Pacifico, "Brush Script MT", cursive',
  GreatVibes: '"Great Vibes", "Brush Script MT", cursive',
  Sacramento: 'Sacramento, "Brush Script MT", cursive',
  Parisienne: 'Parisienne, "Brush Script MT", cursive',
  Lobster: 'Lobster, "Brush Script MT", cursive',
  Courgette: 'Courgette, "Brush Script MT", cursive',
  Satisfy: 'Satisfy, "Brush Script MT", cursive',
  IndieFlower: '"Indie Flower", "Comic Sans MS", cursive',
  AmaticSC: '"Amatic SC", "Comic Sans MS", cursive',
  ShadowsIntoLight: '"Shadows Into Light", "Comic Sans MS", cursive',
  Caveat: 'Caveat, "Comic Sans MS", cursive',
};

export const fontMap = { ...SYSTEM_FONTS, ...WEB_FONTS };

export const DEFAULT_FONT = "Inter";

const GOOGLE_FAMILY_NAMES = {
  PlayfairDisplay: "Playfair Display",
  CormorantGaramond: "Cormorant Garamond",
  CinzelDecorative: "Cinzel Decorative",
  YesevaOne: "Yeseva One",
  AbrilFatface: "Abril Fatface",
  DancingScript: "Dancing Script",
  GreatVibes: "Great Vibes",
  IndieFlower: "Indie Flower",
  AmaticSC: "Amatic SC",
  ShadowsIntoLight: "Shadows Into Light",
  TimesNewRoman: "Times New Roman",
};

export const googleFontHref = (name) => {
  if (!(name in WEB_FONTS)) return null;
  const family = (GOOGLE_FAMILY_NAMES[name] || name).replace(/ /g, "+");
  return `https://fonts.googleapis.com/css2?family=${family}:wght@400;500;600;700&display=swap`;
};

const loaded = new Set();

export const loadFont = (name) => {
  if (!name || loaded.has(name) || name in SYSTEM_FONTS) return;

  const href = googleFontHref(name);
  if (!href || typeof document === "undefined") return;

  loaded.add(name);
  if (document.querySelector(`link[data-font="${name}"]`)) return;

  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = href;
  link.dataset.font = name;
  document.head.appendChild(link);
};

export const loadAllFonts = () => Object.keys(WEB_FONTS).forEach(loadFont);

export const fontGroups = [
  { label: "System", fonts: Object.keys(SYSTEM_FONTS) },
  { label: "Web", fonts: Object.keys(WEB_FONTS) },
];

export const fontLabel = (name) =>
  GOOGLE_FAMILY_NAMES[name] || name.replace(/([a-z])([A-Z])/g, "$1 $2");
