import { Star } from "lucide-react";

const StarInput = ({ value = 0, max = 5, onChange, label = "Rating" }) => {
  const onKeyDown = (event) => {
    const delta =
      { ArrowRight: 1, ArrowUp: 1, ArrowLeft: -1, ArrowDown: -1 }[event.key] ?? 0;
    if (!delta) return;
    event.preventDefault();
    onChange?.(Math.min(max, Math.max(1, (value || 0) + delta)));
  };

  return (
    <div
      role="radiogroup"
      aria-label={label}
      className="flex gap-1"
      onKeyDown={onKeyDown}
    >
      {Array.from({ length: max }, (_, i) => i + 1).map((star) => {
        const filled = star <= value;
        return (
          <button
            key={star}
            type="button"
            role="radio"
            aria-checked={star === value}
            aria-label={`${star} of ${max}`}

            tabIndex={star === (value || 1) ? 0 : -1}
            onClick={() => onChange?.(star)}
            className="rounded p-0.5 transition hover:scale-110"
          >
            <Star
              aria-hidden="true"
              className={`w-5 h-5 ${filled ? "fill-star text-star" : "text-star-empty"}`}
            />
          </button>
        );
      })}
    </div>
  );
};

export default StarInput;
