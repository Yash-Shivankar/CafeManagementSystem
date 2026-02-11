import { Star } from "lucide-react";

const StarDisplay = ({ value = 0, max = 5 }) => {
  return (
    <div className="flex gap-0.5">
      {Array.from({ length: max }, (_, i) => i + 1).map((star) => {
        const filled = star <= value;

        return (
          <Star
            key={star}
            className={`w-4 h-4 ${
              filled ? "fill-yellow-400 text-yellow-400" : "text-gray-400"
            }`}
          />
        );
      })}
    </div>
  );
};
export default StarDisplay;
