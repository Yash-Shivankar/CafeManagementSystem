import { useCallback, useMemo, useRef, useState } from "react";
import { ConfirmContext } from "./useConfirm";
import Modal from "./Modal";
import Button from "./Button";

export const ConfirmProvider = ({ children }) => {
  const [request, setRequest] = useState(null);
  const [reason, setReason] = useState("");
  const resolver = useRef(null);

  const confirm = useCallback((options) => {
    const normalised = typeof options === "string" ? { message: options } : options;
    setRequest({
      title: "Please confirm",
      confirmLabel: "Confirm",
      cancelLabel: "Cancel",
      tone: "primary",
      reasonLabel: null,
      reasonPlaceholder: "",
      ...normalised,
    });
    return new Promise((resolve) => {
      resolver.current = resolve;
    });
  }, []);

  const settle = (answer) => {
    resolver.current?.(answer);
    resolver.current = null;
    setRequest(null);

    setReason("");
  };

  const needsReason = Boolean(request?.reasonLabel);
  const reasonGiven = reason.trim();

  const accept = () => settle(needsReason ? reasonGiven : true);

  const value = useMemo(() => confirm, [confirm]);

  return (
    <ConfirmContext.Provider value={value}>
      {children}

      {request && (
        <Modal title={request.title} onClose={() => settle(false)}>
          <form
            className="space-y-5"
            onSubmit={(event) => {
              event.preventDefault();
              if (needsReason && !reasonGiven) return;
              accept();
            }}
          >
            <p className="text-sm text-muted-foreground">{request.message}</p>

            {needsReason && (
              <div className="space-y-1">
                <label
                  htmlFor="confirm-reason"
                  className="block text-sm font-medium text-foreground"
                >
                  {request.reasonLabel}
                </label>
                <input
                  id="confirm-reason"
                  autoFocus
                  value={reason}
                  onChange={(event) => setReason(event.target.value)}
                  placeholder={request.reasonPlaceholder}
                  className="w-full rounded-md border border-border bg-background px-3 py-2 text-foreground placeholder:text-muted-foreground"
                />
              </div>
            )}

            <div className="flex justify-end gap-2">
              <Button
                label={request.cancelLabel}
                variant="outline"
                size="sm"
                onClick={() => settle(false)}
              />
              <Button
                type="submit"
                label={request.confirmLabel}
                variant={request.tone === "danger" ? "danger" : "primary"}
                size="sm"
                disabled={needsReason && !reasonGiven}
              />
            </div>
          </form>
        </Modal>
      )}
    </ConfirmContext.Provider>
  );
};

export default ConfirmProvider;
