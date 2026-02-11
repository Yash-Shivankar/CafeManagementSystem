import { Star } from "lucide-react";

const StarInput = ({ value = 0, max = 5, onChange }) => (
  <div className="flex gap-1">
    {[...Array(max)].map((_, i) => {
      const star = i + 1;
      const filled = star <= value;

      return (
        <button key={star} type="button" onClick={() => onChange(star)}>
          <Star
            className={`w-5 h-5 ${
              filled ? "fill-yellow-400 text-yellow-400" : "text-gray-400"
            }`}
          />
        </button>
      );
    })}
  </div>
);

export default StarInput;
