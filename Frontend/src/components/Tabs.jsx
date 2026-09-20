import { useRef } from "react";

const Tabs = ({ tabs, activeKey, onChange, label = "Sections" }) => {
  const refs = useRef({});

  const onKeyDown = (event) => {
    const delta = { ArrowRight: 1, ArrowLeft: -1 }[event.key] ?? 0;
    const jump = { Home: 0, End: tabs.length - 1 }[event.key];

    let nextIndex = null;
    if (delta) {
      const current = tabs.findIndex((t) => t.key === activeKey);
      nextIndex = (current + delta + tabs.length) % tabs.length;
    } else if (jump !== undefined) {
      nextIndex = jump;
    }
    if (nextIndex === null) return;

    event.preventDefault();
    const next = tabs[nextIndex];
    onChange(next.key);
    refs.current[next.key]?.focus();
  };

  return (
    <div
      role="tablist"
      aria-label={label}
      onKeyDown={onKeyDown}
      className="flex flex-wrap gap-1 border-b border-border overflow-x-auto"
    >
      {tabs.map(({ key, label: tabLabel }) => {
        const active = key === activeKey;
        return (
          <button
            key={key}
            ref={(el) => {
              refs.current[key] = el;
            }}
            role="tab"
            id={`tab-${key}`}
            aria-selected={active}
            aria-controls={`tabpanel-${key}`}
            tabIndex={active ? 0 : -1}
            onClick={() => onChange(key)}
            className={`
              -mb-px whitespace-nowrap rounded-t-md px-4 py-2 text-sm transition
              ${
                active
                  ? "border-b-2 border-primary font-semibold text-foreground"
                  : "border-b-2 border-transparent text-muted-foreground hover:text-foreground hover:bg-muted"
              }
            `}
          >
            {tabLabel}
          </button>
        );
      })}
    </div>
  );
};

export default Tabs;
