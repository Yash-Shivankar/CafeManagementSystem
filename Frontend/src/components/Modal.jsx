import { useCallback, useEffect, useId, useRef } from "react";

const FOCUSABLE =
  'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])';

const Modal = ({ title, onClose, children }) => {
  const panelRef = useRef(null);
  const previouslyFocused = useRef(null);
  const titleId = `modal-title-${useId()}`;

  const focusables = useCallback(
    () => Array.from(panelRef.current?.querySelectorAll(FOCUSABLE) ?? []),
    [],
  );

  useEffect(() => {
    previouslyFocused.current = document.activeElement;
    const target =
      focusables().find((el) => !el.hasAttribute("data-modal-dismiss")) ??
      panelRef.current;
    target?.focus();
    return () => previouslyFocused.current?.focus?.();
  }, [focusables]);

  useEffect(() => {
    const previous = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = previous;
    };
  }, []);

  const onKeyDown = (event) => {
    if (event.key === "Escape") {
      event.stopPropagation();
      onClose?.();
      return;
    }
    if (event.key !== "Tab") return;

    const items = focusables();
    if (items.length === 0) return;

    const first = items[0];
    const last = items[items.length - 1];

    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{
        backgroundColor: "rgb(var(--color-scrim) / var(--scrim-opacity))",
      }}
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose?.();
      }}
    >
      <div
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        tabIndex={-1}
        onKeyDown={onKeyDown}
        className="
          relative w-full max-w-lg max-h-[90vh] overflow-y-auto
          bg-surface text-foreground
          border border-border
          rounded-xl p-6
          shadow-lg
        "
      >
        <div className="flex items-center justify-between mb-4 gap-4">
          <h2 id={titleId} className="text-xl font-semibold">
            {title}
          </h2>

          <button
            type="button"
            onClick={onClose}
            aria-label="Close dialog"
            data-modal-dismiss=""
            className="
              shrink-0 rounded-md p-1
              text-muted-foreground
              hover:text-foreground hover:bg-muted
              transition
            "
          >
            <span aria-hidden="true" className="text-xl font-bold leading-none">
              &times;
            </span>
          </button>
        </div>

        {children}
      </div>
    </div>
  );
};

export default Modal;
