import { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { Store } from "lucide-react";
import { allSlices } from "../app/allSlices";
import { outletService } from "../services/outlet";

const OutletSwitcher = () => {
  const dispatch = useDispatch();
  const [selected, setSelected] = useState(() => outletService.selected());

  useEffect(() => outletService.subscribe(setSelected), []);

  const options = outletService.available();

  if (!outletService.canSwitch()) {
    return selected ? (
      <span
        className="flex items-center gap-2 text-sm opacity-80"
        title="Your branch"
      >
        <Store size={16} />
        {selected.name}
      </span>
    ) : null;
  }

  const handleChange = (event) => {
    const value = event.target.value;
    outletService.select(value === "" ? null : Number(value));
    dispatch(allSlices.util.resetApiState());
  };

  return (
    <label className="flex items-center gap-2 text-sm">
      <Store size={16} className="shrink-0" />
      <span className="sr-only">Outlet</span>
      <select
        value={selected?.id ?? ""}
        onChange={handleChange}
        className="
          h-9 px-3 rounded-md
          bg-surface text-text
          border border-border
          focus:outline-none focus:ring-2 focus:ring-primary
          transition
        "
      >
        <option value="">All outlets</option>
        {options.map((outlet) => (
          <option key={outlet.id} value={outlet.id}>
            {outlet.name} ({outlet.code})
          </option>
        ))}
      </select>
    </label>
  );
};

export default OutletSwitcher;
