const Button = ({
  label,
  onClick,
  type = "button",
  variant = "primary",
  size = "md",
  disabled = false,
  icon: Icon,
}) => {
  const base =
    "inline-flex items-center gap-2 font-medium rounded-md transition-all focus:outline-none";

  const variants = {
    primary: "bg-primary text-white hover:bg-primary-dark",
    secondary: "bg-secondary text-white hover:bg-secondary-dark",
    outline: "border border-border text-text hover:bg-background",
    danger: "bg-error text-white hover:opacity-90",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-2",
    lg: "px-5 py-2.5 text-lg",
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${base} ${variants[variant]} ${sizes[size]} ${
        disabled ? "opacity-50 cursor-not-allowed" : ""
      }`}
    >
      {Icon && <Icon size={16} />}
      {label}
    </button>
  );
};

export default Button;
