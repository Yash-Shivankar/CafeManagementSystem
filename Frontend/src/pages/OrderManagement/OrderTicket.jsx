import { useState } from "react";
import { toast } from "react-toastify";
import { Minus, Plus, Trash2 } from "lucide-react";

import Button from "../../components/Button";
import Modal from "../../components/Modal";
import { useConfirm } from "../../components/useConfirm";
import { usePermissions } from "../../services/usePermissions";
import { formatMoney, formatEnum } from "../../utils/format";
import {
  useBillOrderMutation,
  useCreatePaymentMutation,
  useCancelOrderMutation,
  useConfirmOrderMutation,
  useRemoveOrderItemMutation,
  useUpdateOrderItemMutation,
} from "../../app/allSlices";

const TENDERS = [
  { value: "cash", label: "Cash" },
  { value: "upi", label: "UPI" },
  { value: "card", label: "Card" },
];

const STATUS_TONE = {
  open: "bg-muted text-muted-foreground",
  confirmed: "bg-info/15 text-info",
  served: "bg-success/15 text-success",
  billed: "bg-primary/15 text-primary",
  cancelled: "bg-error/15 text-error",
};

const Row = ({ label, value, strong = false, muted = false }) => (
  <div
    className={`flex items-center justify-between text-sm ${
      strong ? "font-semibold text-foreground" : muted ? "text-muted-foreground" : "text-foreground"
    }`}
  >
    <span>{label}</span>
    <span className="tabular-nums">{value}</span>
  </div>
);

const OrderTicket = ({ order, onBilled }) => {
  const confirm = useConfirm();
  const { canDelete } = usePermissions();

  const [billing, setBilling] = useState(false);
  const [discount, setDiscount] = useState("");
  const [serviceCharge, setServiceCharge] = useState("");

  const [settling, setSettling] = useState(null);

  const [updateItem] = useUpdateOrderItemMutation();
  const [removeItem] = useRemoveOrderItemMutation();
  const [confirmOrder, { isLoading: confirming }] = useConfirmOrderMutation();
  const [billOrder, { isLoading: raisingBill }] = useBillOrderMutation();
  const [cancelOrder] = useCancelOrderMutation();
  const [createPayment, { isLoading: settlingPayment }] = useCreatePaymentMutation();

  if (!order) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 p-8 text-center">
        <p className="font-medium text-foreground">No order open</p>
        <p className="max-w-xs text-sm text-muted-foreground">
          Pick a table to start one, or open a takeaway.
        </p>
      </div>
    );
  }

  const isOpen = order.status === "open";
  const totals = order.totals ?? {};
  const live = (order.items ?? []).filter((item) => item.status !== "cancelled");

  const changeQuantity = async (item, delta) => {
    const next = Number(item.quantity) + delta;
    if (next <= 0) {
      return removeLine(item);
    }
    try {
      await updateItem({
        orderId: order.id,
        itemId: item.id,
        quantity: String(next),
      }).unwrap();
    } catch (error) {
      toast.error(error?.data?.detail || "Could not change the quantity");
    }
  };

  const removeLine = async (item) => {
    try {
      await removeItem({ orderId: order.id, itemId: item.id }).unwrap();
    } catch (error) {
      toast.error(error?.data?.detail || "Could not remove the line");
    }
  };

  const send = async () => {
    try {
      await confirmOrder(order.id).unwrap();
      toast.success("Sent to the kitchen");
    } catch (error) {
      toast.error(error?.data?.detail || "Could not send the order");
    }
  };

  const raiseBill = async () => {
    try {
      const invoice = await billOrder({
        id: order.id,
        discount_amount: discount || undefined,
        service_charge_percent: serviceCharge || undefined,
      }).unwrap();

      setBilling(false);
      setDiscount("");
      setServiceCharge("");

      setSettling(invoice);
    } catch (error) {
      toast.error(error?.data?.detail || "Could not raise the bill");
    }
  };

  const settle = async (method) => {
    try {
      await createPayment({
        invoice_id: settling.id,
        amount: String(settling.total_amount),
        method,
      }).unwrap();

      toast.success(
        `${settling.invoice_number} settled — ${formatMoney(settling.total_amount)} by ${method}`,
      );
      setSettling(null);
      onBilled?.(settling);
    } catch (error) {
      toast.error(error?.data?.detail || "Could not record the payment");
    }
  };

  const voidOrder = async () => {
    const reason = await confirm({
      title: `Cancel order ${order.order_number}?`,
      message:
        "Every line still on it is voided. The order and its lines are kept with the reason — a dish that was cooked and then cancelled is what a wastage report is made of.",
      tone: "danger",
      confirmLabel: "Cancel order",
      reasonLabel: "Why is it being cancelled?",
      reasonPlaceholder: "Customer left, wrong order, kitchen error…",
    });
    if (!reason) return;

    try {
      await cancelOrder({ id: order.id, reason }).unwrap();
      toast.success("Order cancelled");
    } catch (error) {
      toast.error(error?.data?.detail || "Could not cancel the order");
    }
  };

  return (
    <div className="flex h-full flex-col">
      <header className="flex items-start justify-between gap-3 border-b border-border p-4">
        <div>
          <p className="font-semibold text-foreground">{order.order_number}</p>
          <p className="text-xs text-muted-foreground">
            {formatEnum(order.order_type)}
            {order.guest_count ? ` · ${order.guest_count} covers` : ""}
          </p>
        </div>
        <span
          className={`rounded-full px-2.5 py-1 text-xs font-medium ${
            STATUS_TONE[order.status] ?? "bg-muted text-muted-foreground"
          }`}
        >
          {formatEnum(order.status)}
        </span>
      </header>

      <div className="flex-1 overflow-y-auto p-4">
        {live.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">
            Nothing on this order yet. Tap an item to add it.
          </p>
        ) : (
          <ul className="space-y-4 divide-y divide-border [&>li]:pt-4 [&>li:first-child]:pt-0">
            {live.map((item) => (
              <li key={item.id} className="space-y-1.5">
                <div className="flex items-baseline justify-between gap-3">
                  <p className="min-w-0 flex-1 text-sm font-medium text-foreground">
                    {item.item_name}
                  </p>
                  <span className="shrink-0 text-sm tabular-nums text-foreground">
                    {formatMoney(Number(item.unit_price) * Number(item.quantity))}
                  </span>
                </div>

                <div className="flex items-center justify-between gap-2">
                  <p className="min-w-0 truncate text-xs text-muted-foreground">
                    {formatMoney(item.unit_price)} · {Number(item.tax_rate)}% GST
                    {item.status !== "pending" && ` · ${formatEnum(item.status)}`}
                  </p>

                  {isOpen ? (
                    <div className="flex shrink-0 items-center gap-1">
                      <Button
                        icon={Minus}
                        size="sm"
                        variant="outline"
                        ariaLabel={`Reduce ${item.item_name}`}
                        title={`Reduce ${item.item_name}`}
                        onClick={() => changeQuantity(item, -1)}
                      />
                      <span className="w-6 text-center text-sm tabular-nums text-foreground">
                        {Number(item.quantity)}
                      </span>
                      <Button
                        icon={Plus}
                        size="sm"
                        variant="outline"
                        ariaLabel={`Add another ${item.item_name}`}
                        title={`Add another ${item.item_name}`}
                        onClick={() => changeQuantity(item, 1)}
                      />
                      <Button
                        icon={Trash2}
                        size="sm"
                        variant="ghost"
                        ariaLabel={`Remove ${item.item_name}`}
                        title={`Remove ${item.item_name}`}
                        onClick={() => removeLine(item)}
                      />
                    </div>
                  ) : (
                    <span className="shrink-0 text-sm tabular-nums text-muted-foreground">
                      x{Number(item.quantity)}
                    </span>
                  )}
                </div>

                {item.notes && (
                  <p className="text-xs italic text-muted-foreground">{item.notes}</p>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>

      <footer className="space-y-3 border-t border-border p-4">
        <Row label="Subtotal" value={formatMoney(totals.subtotal)} />
        {Number(totals.discount_amount) > 0 && (
          <Row label="Discount" value={`- ${formatMoney(totals.discount_amount)}`} muted />
        )}
        {Number(totals.service_charge) > 0 && (
          <Row label="Service charge" value={formatMoney(totals.service_charge)} muted />
        )}
        <Row label="CGST" value={formatMoney(totals.cgst_amount)} muted />
        <Row label="SGST" value={formatMoney(totals.sgst_amount)} muted />
        {Number(totals.round_off) !== 0 && (
          <Row label="Round off" value={formatMoney(totals.round_off)} muted />
        )}
        <div className="border-t border-border pt-2">
          <Row label="Total" value={formatMoney(totals.grand_total)} strong />
        </div>

        <div className="flex flex-wrap gap-2 pt-1">
          {isOpen && (
            <Button
              label="Send to kitchen"
              className="flex-1"
              loading={confirming}
              disabled={live.length === 0}
              onClick={send}
            />
          )}
          {["confirmed", "served"].includes(order.status) && (
            <Button
              label="Bill"
              className="flex-1"
              loading={raisingBill}
              onClick={() => setBilling(true)}
            />
          )}
          {["open", "confirmed", "served"].includes(order.status) && canDelete("orders") && (
            <Button label="Cancel order" variant="outline" onClick={voidOrder} />
          )}
        </div>
      </footer>

      {settling && (
        <Modal
          title={`Take payment — ${settling.invoice_number}`}
          onClose={() => {
            setSettling(null);
            onBilled?.(settling);
          }}
        >
          <div className="space-y-5">
            <div className="rounded-md border border-border bg-background p-4 text-center">
              <p className="text-xs uppercase tracking-wide text-muted-foreground">Due</p>
              <p className="text-3xl font-semibold tabular-nums text-foreground">
                {formatMoney(settling.total_amount)}
              </p>
              <p className="mt-1 text-xs text-muted-foreground">
                incl. {formatMoney(settling.tax_amount)} GST
                {Number(settling.round_off) !== 0 &&
                  ` · round off ${formatMoney(settling.round_off)}`}
              </p>
            </div>

            <div className="grid grid-cols-3 gap-2">
              {TENDERS.map((tender) => (
                <Button
                  key={tender.value}
                  label={tender.label}
                  className="h-14"
                  loading={settlingPayment}
                  onClick={() => settle(tender.value)}
                />
              ))}
            </div>

            <p className="text-center text-xs text-muted-foreground">
              Part payments and split bills are recorded from the Payments
              screen against this invoice number.
            </p>
          </div>
        </Modal>
      )}

      {billing && (
        <Modal title={`Bill ${order.order_number}`} onClose={() => setBilling(false)}>
          <div className="space-y-4">
            <div className="space-y-1">
              <label htmlFor="bill-discount" className="text-sm font-medium text-foreground">
                Discount
              </label>
              <input
                id="bill-discount"
                type="number"
                min="0"
                step="0.01"
                value={discount}
                onChange={(event) => setDiscount(event.target.value)}
                className="w-full rounded-md border border-border bg-background px-3 py-2 text-foreground"
                placeholder="0.00"
              />
              <p className="text-xs text-muted-foreground">
                Taken off before GST, spread across the lines — so the tax comes
                down with it.
              </p>
            </div>

            <div className="space-y-1">
              <label htmlFor="bill-service" className="text-sm font-medium text-foreground">
                Service charge %
              </label>
              <input
                id="bill-service"
                type="number"
                min="0"
                max="100"
                step="0.5"
                value={serviceCharge}
                onChange={(event) => setServiceCharge(event.target.value)}
                className="w-full rounded-md border border-border bg-background px-3 py-2 text-foreground"
                placeholder="0"
              />
              <p className="text-xs text-muted-foreground">
                Optional, and taxable. A tip is not charged on the bill at all.
              </p>
            </div>

            <div className="flex justify-end gap-2">
              <Button label="Back" variant="outline" onClick={() => setBilling(false)} />
              <Button label="Raise bill" loading={raisingBill} onClick={raiseBill} />
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default OrderTicket;
