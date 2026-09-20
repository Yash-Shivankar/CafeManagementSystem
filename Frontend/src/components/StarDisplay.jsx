import { Star } from "lucide-react";

const StarDisplay = ({ value = 0, max = 5 }) => (
  <div className="flex gap-0.5" role="img" aria-label={`${value} out of ${max}`}>
    {Array.from({ length: max }, (_, i) => i + 1).map((star) => (
      <Star
        key={star}
        aria-hidden="true"
        className={`w-4 h-4 ${
          star <= value ? "fill-star text-star" : "text-star-empty"
        }`}
      />
    ))}
  </div>
);

export default StarDisplay;
