const Button = ({
  label,
  onClick,
  type = "button",
  variant = "primary",
  size = "md",
  disabled = false,
  loading = false,
  icon: Icon,
  className = "",
  title,
  ariaLabel,
}) => {
  const base =
    "inline-flex items-center justify-center gap-2 font-medium rounded-md transition " +
    "disabled:opacity-50 disabled:cursor-not-allowed";

  const variants = {
    primary: "bg-primary text-on-primary hover:bg-primary-dark",
    secondary: "bg-secondary text-on-secondary hover:bg-secondary-dark",
    outline: "border border-border text-foreground hover:bg-muted",
    danger: "bg-error text-on-error hover:brightness-110",
    ghost: "text-muted-foreground hover:bg-muted hover:text-foreground",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-2",
    lg: "px-5 py-2.5 text-lg",
  };

  const isDisabled = disabled || loading;

  const accessibleName = ariaLabel || (!label ? title : undefined);

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={isDisabled}
      title={title}
      aria-label={accessibleName}
      aria-busy={loading || undefined}
      className={`${base} ${variants[variant] ?? variants.primary} ${sizes[size] ?? sizes.md} ${className}`}
    >
      {loading ? (
        <span
          aria-hidden="true"
          className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"
        />
      ) : (
        Icon && <Icon size={16} aria-hidden="true" />
      )}
      {label}
    </button>
  );
};

export default Button;
