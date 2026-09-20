const ICON_SIZE_MAP = {
  sm: "h-4 w-4",
  md: "h-5 w-5",
  lg: "h-6 w-6",
  xl: "h-7 w-7",
  xxl: "h-10 w-10",
};

const StatsCard = ({
  label,
  value,
  description,
  icon: Icon,
  iconSize = "md",
  loading = false,
  className = "",
}) => {
  return (
    <div
      className={`
        relative
        rounded-md
        border border-border
        bg-surface/60
        backdrop-blur-lg
        px-6 py-5
        shadow-sm
        transition
        hover:bg-surface/80
        ${className}
      `}
    >

      <div
        className="pointer-events-none absolute inset-0 rounded-md"
        style={{
          backgroundImage:
            "linear-gradient(to bottom right, rgb(var(--color-sheen) / var(--sheen-opacity)), transparent)",
        }}
      />

      <div className="relative flex h-full flex-col justify-between">

        <div className="flex items-start justify-between">
          <p className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
            {label}
          </p>

          {Icon && (
            <div className="flex h-10 w-10 items-center justify-center rounded-md bg-muted/40">
              <Icon
                className={`${ICON_SIZE_MAP[iconSize]} text-muted-foreground`}
              />
            </div>
          )}
        </div>

        {loading ? (
          <div className="h-8 w-24 rounded bg-muted animate-pulse" />
        ) : (
          <div className="text-3xl font-semibold text-foreground">
            {value ?? "—"}
          </div>
        )}

        {description && !loading && (
          <p className="text-sm text-muted-foreground">{description}</p>
        )}
      </div>
    </div>
  );
};

export default StatsCard;
