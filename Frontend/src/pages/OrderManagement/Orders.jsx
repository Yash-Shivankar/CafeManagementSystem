import { useMemo, useState } from "react";
import { toast } from "react-toastify";

import Button from "../../components/Button";
import Modal from "../../components/Modal";
import { usePermissions } from "../../services/usePermissions";
import { formatMoney, formatEnum } from "../../utils/format";
import OrderTicket from "./OrderTicket";
import {
  useAddOrderItemMutation,
  useUpdateOrderItemMutation,
  useGetMenuCategoriesQuery,
  useGetMenuItemsQuery,
  useGetOrderByIdQuery,
  useGetOrdersQuery,
  useGetTablesQuery,
  useOpenOrderMutation,
} from "../../app/allSlices";

const LIVE_STATUSES = ["open", "confirmed", "served"];

const MENU_PAGE_SIZE = 100;

const Orders = () => {
  const { canCreate } = usePermissions();

  const [selectedId, setSelectedId] = useState(null);
  const [opening, setOpening] = useState(false);
  const [categoryId, setCategoryId] = useState("");

  const { data: orderData, isFetching: loadingOrders } = useGetOrdersQuery(
    { limit: 50 },
    { pollingInterval: 15000 },
  );

  const { currentData: order } = useGetOrderByIdQuery(selectedId, { skip: !selectedId });

  const { data: menuData } = useGetMenuItemsQuery({
    limit: MENU_PAGE_SIZE,
    is_available: true,
    ...(categoryId ? { category_id: categoryId } : {}),
  });
  const { data: categoryData } = useGetMenuCategoriesQuery({ limit: MENU_PAGE_SIZE });
  const { data: tableData } = useGetTablesQuery({ limit: MENU_PAGE_SIZE });

  const [openOrder, { isLoading: creating }] = useOpenOrderMutation();
  const [addItem] = useAddOrderItemMutation();
  const [updateItem] = useUpdateOrderItemMutation();

  const liveOrders = useMemo(
    () => (orderData?.data ?? []).filter((row) => LIVE_STATUSES.includes(row.status)),
    [orderData],
  );

  const occupiedTableIds = useMemo(
    () => new Set(liveOrders.map((row) => row.table_id).filter(Boolean)),
    [liveOrders],
  );

  const items = menuData?.data ?? [];

  const start = async ({ orderType, tableId }) => {
    try {
      const created = await openOrder({
        order_type: orderType,
        table_id: tableId ?? null,
        items: [],
      }).unwrap();
      setSelectedId(created.id);
      setOpening(false);
      toast.success(`Order ${created.order_number} opened`);
    } catch (error) {
      toast.error(error?.data?.detail || "Could not open the order");
    }
  };

  const tap = async (item) => {
    if (!order) {
      toast.info("Open an order first");
      return;
    }
    if (order.status !== "open") {
      toast.info("This order has gone to the kitchen. Open a new one for extras.");
      return;
    }

    const existing = (order.items ?? []).find(
      (line) =>
        line.menu_item_id === item.id &&
        line.status === "pending" &&
        !line.notes,
    );

    try {
      if (existing) {
        await updateItem({
          orderId: order.id,
          itemId: existing.id,
          quantity: String(Number(existing.quantity) + 1),
        }).unwrap();
      } else {
        await addItem({ orderId: order.id, menu_item_id: item.id, quantity: "1" }).unwrap();
      }
    } catch (error) {
      toast.error(error?.data?.detail || `Could not add ${item.name}`);
    }
  };

  return (
    <div className="flex h-[calc(100vh-7rem)] flex-col gap-4 p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Orders</h1>
          <p className="text-sm text-muted-foreground">
            {liveOrders.length} running
          </p>
        </div>
        {canCreate("orders") && (
          <Button label="New order" onClick={() => setOpening(true)} />
        )}
      </div>

      <div className="shrink-0">
        {liveOrders.length === 0 && !loadingOrders ? (
          <p className="rounded-md border border-dashed border-border px-4 py-3 text-sm text-muted-foreground">
            Nothing running. Start an order to begin the shift.
          </p>
        ) : (
          <ul className="flex gap-2 overflow-x-auto pb-1">
            {liveOrders.map((row) => (
              <li key={row.id} className="shrink-0">
                <button
                  type="button"
                  onClick={() => setSelectedId(row.id)}
                  aria-pressed={row.id === selectedId}
                  className={`rounded-md border px-4 py-2 text-left transition ${
                    row.id === selectedId
                      ? "border-primary bg-muted"
                      : "border-border hover:border-primary"
                  }`}
                >
                  <span className="block text-sm font-medium text-foreground">
                    {row.order_number}
                  </span>
                  <span className="block text-xs text-muted-foreground">
                    {row.table_id ? `Table ${row.table_id}` : formatEnum(row.order_type)} ·{" "}
                    {formatEnum(row.status)}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="grid min-h-0 flex-1 gap-4 lg:grid-cols-[1fr_20rem] xl:grid-cols-[1fr_24rem]">

        <section className="flex min-h-0 flex-col rounded-md border border-border bg-surface">
          <div className="flex flex-wrap gap-1 border-b border-border p-3">
            <button
              type="button"
              onClick={() => setCategoryId("")}
              aria-pressed={categoryId === ""}
              className={`rounded-md px-3 py-1.5 text-sm transition ${
                categoryId === ""
                  ? "bg-primary text-on-primary"
                  : "text-muted-foreground hover:bg-muted"
              }`}
            >
              All
            </button>
            {(categoryData?.data ?? []).map((category) => (
              <button
                key={category.id}
                type="button"
                onClick={() => setCategoryId(String(category.id))}
                aria-pressed={categoryId === String(category.id)}
                className={`whitespace-nowrap rounded-md px-3 py-1.5 text-sm transition ${
                  categoryId === String(category.id)
                    ? "bg-primary text-on-primary"
                    : "text-muted-foreground hover:bg-muted"
                }`}
              >
                {category.name}
              </button>
            ))}
          </div>

          <div className="min-h-0 flex-1 overflow-y-auto p-3">
            {items.length === 0 ? (
              <p className="py-10 text-center text-sm text-muted-foreground">
                Nothing available in this section.
              </p>
            ) : (
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
                {items.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => tap(item)}
                    className="flex h-24 flex-col justify-between rounded-md border border-border bg-background p-3 text-left transition hover:border-primary"
                  >
                    <span className="line-clamp-2 text-sm font-medium leading-tight text-foreground">
                      {item.name}
                    </span>
                    <span className="flex items-center justify-between gap-1 text-xs">
                      <span className="tabular-nums text-foreground">
                        {formatMoney(item.price)}
                      </span>
                      <span
                        className={item.is_veg ? "text-success" : "text-error"}

                        title={item.is_veg ? "Vegetarian" : "Non-vegetarian"}
                      >
                        {item.is_veg ? "Veg" : "Non-veg"}
                      </span>
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </section>

        <aside className="min-h-0 overflow-hidden rounded-md border border-border bg-surface">
          <OrderTicket order={order} onBilled={() => setSelectedId(null)} />
        </aside>
      </div>

      {opening && (
        <Modal title="New order" onClose={() => setOpening(false)}>
          <div className="space-y-5">
            <div className="space-y-2">
              <p className="text-sm font-medium text-foreground">Dine in — pick a table</p>
              <div className="grid grid-cols-3 gap-2 sm:grid-cols-4">
                {(tableData?.data ?? []).map((table) => {
                  const busy = occupiedTableIds.has(table.id);
                  return (
                    <button
                      key={table.id}
                      type="button"
                      disabled={busy || creating}
                      onClick={() => start({ orderType: "dine-in", tableId: table.id })}
                      title={busy ? "This table already has an order running" : undefined}
                      className="rounded-md border border-border p-3 text-sm transition enabled:hover:border-primary disabled:opacity-40 disabled:cursor-not-allowed"
                    >
                      <span className="block font-medium text-foreground">
                        {table.table_number}
                      </span>
                      <span className="block text-xs text-muted-foreground">
                        {busy ? "Occupied" : `${table.seating_capacity} seats`}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="flex gap-2 border-t border-border pt-4">
              <Button
                label="Takeaway"
                variant="outline"
                className="flex-1"
                loading={creating}
                onClick={() => start({ orderType: "takeaway" })}
              />
              <Button
                label="Delivery"
                variant="outline"
                className="flex-1"
                loading={creating}
                onClick={() => start({ orderType: "delivery" })}
              />
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default Orders;
