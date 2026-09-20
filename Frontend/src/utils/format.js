export const DISPLAY_TIME_ZONE = "Asia/Kolkata";

export const NUMBER_LOCALE = "en-IN";

export const EMPTY = "—";

const isBlank = (value) => value === null || value === undefined || value === "";

const toNumber = (value) => {
  if (isBlank(value)) return null;
  const n = typeof value === "number" ? value : Number(String(value).replace(/,/g, ""));
  return Number.isFinite(n) ? n : null;
};

const toDate = (value) => {
  if (isBlank(value)) return null;

  const raw = typeof value === "string" && /^\d{4}-\d{2}-\d{2}$/.test(value)
    ? `${value}T12:00:00`
    : value;
  const date = raw instanceof Date ? raw : new Date(raw);
  return Number.isNaN(date.getTime()) ? null : date;
};

export const formatMoney = (value, { currency = "INR", decimals = 2 } = {}) => {
  const n = toNumber(value);
  if (n === null) return EMPTY;

  return new Intl.NumberFormat(NUMBER_LOCALE, {
    style: "currency",
    currency,
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(n);
};

export const formatNumber = (value, { decimals = 0 } = {}) => {
  const n = toNumber(value);
  if (n === null) return EMPTY;
  return new Intl.NumberFormat(NUMBER_LOCALE, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(n);
};

export const formatQuantity = (value) => {
  const n = toNumber(value);
  if (n === null) return EMPTY;
  return formatNumber(n, { decimals: Number.isInteger(n) ? 0 : 3 });
};

export const formatPercent = (value, { decimals = 1 } = {}) => {
  const n = toNumber(value);
  if (n === null) return EMPTY;
  return `${formatNumber(n, { decimals })}%`;
};

const MONTHS = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

const zonedParts = (date) => {
  const parts = new Intl.DateTimeFormat("en-GB", {
    year: "numeric",
    month: "numeric",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
    timeZone: DISPLAY_TIME_ZONE,
  }).formatToParts(date);

  const get = (type) => parts.find((part) => part.type === type)?.value ?? "";

  const hour24 = Number(get("hour")) % 24;

  return {
    year: get("year"),
    month: Number(get("month")),
    day: get("day"),
    hour24,
    minute: get("minute"),
  };
};

const clockOf = ({ hour24, minute }) => {
  const suffix = hour24 < 12 ? "am" : "pm";
  const hour12 = hour24 % 12 === 0 ? 12 : hour24 % 12;
  return `${String(hour12).padStart(2, "0")}:${minute} ${suffix}`;
};

export const formatDate = (value) => {
  const date = toDate(value);
  if (!date) return EMPTY;
  const p = zonedParts(date);
  return `${p.day} ${MONTHS[p.month - 1]} ${p.year}`;
};

export const formatDateTime = (value) => {
  const date = toDate(value);
  if (!date) return EMPTY;
  return `${formatDate(value)}, ${clockOf(zonedParts(date))}`;
};

export const formatTime = (value) => {
  const date = toDate(value);
  if (!date) return EMPTY;
  return clockOf(zonedParts(date));
};

export const todayISO = () => {
  const parts = new Intl.DateTimeFormat("en-CA", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    timeZone: DISPLAY_TIME_ZONE,
  }).formatToParts(new Date());
  const get = (type) => parts.find((p) => p.type === type)?.value;
  return `${get("year")}-${get("month")}-${get("day")}`;
};

export const formatEnum = (value) => {
  if (isBlank(value)) return EMPTY;
  const words = String(value).replace(/[_-]+/g, " ").trim().toLowerCase();
  return words.charAt(0).toUpperCase() + words.slice(1);
};

export const formatName = (person) => {
  if (!person) return EMPTY;
  if (typeof person === "string") return person;
  const name =
    person.full_name ||
    [person.first_name, person.last_name].filter(Boolean).join(" ") ||
    person.name ||
    person.username ||
    person.email;
  return name || EMPTY;
};
