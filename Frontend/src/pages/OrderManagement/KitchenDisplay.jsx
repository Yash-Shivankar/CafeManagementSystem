import { toast } from "react-toastify";

import Button from "../../components/Button";
import { useConfirm } from "../../components/useConfirm";
import { formatEnum } from "../../utils/format";
import {
  useGetKitchenQueueQuery,
  useSetOrderItemStatusMutation,
} from "../../app/allSlices";

const REFRESH_MS = 10000;

const urgency = (seconds) => {
  if (seconds == null) return "border-border";
  if (seconds > 600) return "border-error";
  if (seconds > 300) return "border-warning";
  return "border-border";
};

const waitingLabel = (seconds) => {
  if (seconds == null) return "—";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes} min`;
  return `${Math.floor(minutes / 60)}h ${minutes % 60}m`;
};

const KitchenDisplay = () => {
  const confirm = useConfirm();

  const { data, isLoading } = useGetKitchenQueueQuery(
    { limit: 200 },
    { pollingInterval: REFRESH_MS, refetchOnFocus: true },
  );

  const [setStatus] = useSetOrderItemStatusMutation();

  const move = async (ticket, status) => {
    try {
      await setStatus({
        orderId: ticket.order_id,
        itemId: ticket.order_item_id,
        status,
      }).unwrap();
    } catch (error) {
      toast.error(error?.data?.detail || "Could not update the ticket");
    }
  };

  const void_ = async (ticket) => {
    const reason = await confirm({
      title: `Cancel ${ticket.item_name}?`,
      message:
        "The line stays on the order as cancelled, with this reason — a dish that was started and then voided is what a wastage report is made of.",
      tone: "danger",
      confirmLabel: "Cancel item",
      reasonLabel: "Why?",
      reasonPlaceholder: "Out of stock, spoiled, customer changed their mind…",
    });
    if (!reason) return;

    try {
      await setStatus({
        orderId: ticket.order_id,
        itemId: ticket.order_item_id,
        status: "cancelled",
        reason,
      }).unwrap();
    } catch (error) {
      toast.error(error?.data?.detail || "Could not cancel the item");
    }
  };

  const tickets = data?.tickets ?? [];

  return (
    <div className="space-y-4 p-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Kitchen</h1>
          <p className="text-sm text-muted-foreground">
            Oldest first · refreshes every {REFRESH_MS / 1000} seconds
          </p>
        </div>
        <p className="text-sm text-muted-foreground" aria-live="polite">
          {tickets.length} {tickets.length === 1 ? "ticket" : "tickets"} on
        </p>
      </div>

      {isLoading && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {Array.from({ length: 4 }, (_, i) => (
            <div key={i} className="h-40 animate-pulse rounded-md bg-muted" />
          ))}
        </div>
      )}

      {!isLoading && tickets.length === 0 && (
        <div className="flex flex-col items-center gap-2 rounded-md border border-border bg-surface px-6 py-16 text-center">
          <p className="text-lg font-medium text-foreground">The pass is clear</p>
          <p className="max-w-sm text-sm text-muted-foreground">
            Tickets appear here the moment an order is sent from the till.
          </p>
        </div>
      )}

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {tickets.map((ticket) => (
          <article
            key={ticket.order_item_id}
            className={`flex flex-col gap-3 rounded-md border-2 bg-surface p-4 ${urgency(
              ticket.waiting_seconds,
            )}`}
          >
            <header className="flex items-start justify-between gap-2">
              <div className="min-w-0">
                <p className="truncate text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  {ticket.table_number
                    ? `Table ${ticket.table_number}`
                    : formatEnum(ticket.order_type)}
                </p>
                <p className="truncate text-xs text-muted-foreground">{ticket.order_number}</p>
              </div>
              <span className="shrink-0 text-right text-sm font-semibold tabular-nums text-foreground">
                {waitingLabel(ticket.waiting_seconds)}
              </span>
            </header>

            <div className="flex-1">
              <p className="text-lg font-semibold leading-tight text-foreground">
                {Number(ticket.quantity)} × {ticket.item_name}
              </p>
              {ticket.notes && (
                <p className="mt-1 rounded bg-warning/15 px-2 py-1 text-sm text-foreground">
                  {ticket.notes}
                </p>
              )}
              {ticket.prep_minutes ? (
                <p className="mt-1 text-xs text-muted-foreground">
                  Usually {ticket.prep_minutes} min
                </p>
              ) : null}
            </div>

            <div className="flex flex-wrap gap-2">
              {ticket.status === "fired" && (
                <Button
                  label="Ready"
                  size="sm"
                  className="flex-1"
                  onClick={() => move(ticket, "ready")}
                />
              )}
              {ticket.status === "ready" && (
                <Button
                  label="Served"
                  size="sm"
                  className="flex-1"
                  onClick={() => move(ticket, "served")}
                />
              )}
              <Button label="Void" size="sm" variant="ghost" onClick={() => void_(ticket)} />
            </div>
          </article>
        ))}
      </div>
    </div>
  );
};

export default KitchenDisplay;
