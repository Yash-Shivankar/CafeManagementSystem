import { Inbox } from "lucide-react";
import Button from "./Button";

const SKELETON_ROWS = 5;

const DataTable = ({
  data = [],
  columns = [],
  onEdit,
  onDelete,
  pagination = {},
  onPageChange,
  loading = false,
  caption,
  emptyMessage = "Nothing here yet",
  emptyHint,
  emptyAction,
  getRowId = (row, index) => row?.id ?? `row-${index}`,
  rowActions,
}) => {
  const tableColumns = columns.length
    ? columns
    : data.length
      ? Object.keys(data[0]).map((k) => ({ key: k, label: k }))
      : [];

  const { currentPage = 1, totalPages = 1, total } = pagination;
  const hasActions = Boolean(onEdit || onDelete || rowActions);
  const isEmpty = !loading && data.length === 0;

  const headCell =
    "px-4 py-3 font-semibold text-xs tracking-wide uppercase " +
    "border-b border-border text-muted-foreground bg-muted";

  const renderCell = (col, row) =>
    col.render ? col.render(row[col.key], row) : row[col.key];

  const actions = (row) => (
    <div className="flex items-center justify-center gap-2 whitespace-nowrap">
      {rowActions?.(row)}
      {onEdit && <Button label="Edit" size="sm" variant="outline" onClick={() => onEdit(row)} />}
      {onDelete && (
        <Button label="Delete" size="sm" variant="danger" onClick={() => onDelete(row)} />
      )}
    </div>
  );

  return (
    <div className="rounded-md border border-border bg-surface">

      <div className="hidden md:block overflow-x-auto">
        <table className="w-full table-fixed border-collapse text-sm text-foreground">
          {caption && <caption className="sr-only">{caption}</caption>}
          <thead>
            <tr>
              {tableColumns.map((col) => (
                <th key={col.key} scope="col" className={`${headCell} text-left`}>
                  {col.label}
                </th>
              ))}
              {hasActions && (
                <th scope="col" className={`${headCell} text-center w-44`}>
                  Actions
                </th>
              )}
            </tr>
          </thead>

          <tbody aria-busy={loading || undefined}>
            {loading &&
              Array.from({ length: SKELETON_ROWS }, (_, i) => (
                <tr key={`skeleton-${i}`}>
                  {[...tableColumns, ...(hasActions ? [{ key: "__actions" }] : [])].map((col) => (
                    <td key={col.key} className="px-4 py-3 border-b border-border">
                      <div className="h-4 rounded bg-muted animate-pulse" />
                    </td>
                  ))}
                </tr>
              ))}

            {!loading &&
              data.map((row, i) => (
                <tr key={getRowId(row, i)} className="transition hover:bg-muted/50">
                  {tableColumns.map((col) => (
                    <td
                      key={col.key}
                      className="px-4 py-2 border-b border-border max-w-[220px]"
                    >
                      <div
                        className="truncate"
                        title={col.render ? undefined : row[col.key]}
                      >
                        {renderCell(col, row)}
                      </div>
                    </td>
                  ))}

                  {hasActions && (
                    <td className="px-4 py-2 border-b border-border">{actions(row)}</td>
                  )}
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      <div className="md:hidden divide-y divide-border">
        {loading &&
          Array.from({ length: SKELETON_ROWS }, (_, i) => (
            <div key={`skeleton-card-${i}`} className="p-4 space-y-2">
              <div className="h-4 w-1/3 rounded bg-muted animate-pulse" />
              <div className="h-4 w-2/3 rounded bg-muted animate-pulse" />
            </div>
          ))}

        {!loading &&
          data.map((row, i) => (
            <div key={getRowId(row, i)} className="p-4 space-y-2">
              <dl className="space-y-1">
                {tableColumns.map((col) => (
                  <div key={col.key} className="flex gap-3 text-sm">
                    <dt className="w-32 shrink-0 text-xs uppercase tracking-wide text-muted-foreground pt-0.5">
                      {col.label}
                    </dt>
                    <dd className="min-w-0 flex-1 break-words text-foreground">
                      {renderCell(col, row)}
                    </dd>
                  </div>
                ))}
              </dl>
              {hasActions && <div className="pt-1">{actions(row)}</div>}
            </div>
          ))}
      </div>

      {isEmpty && (
        <div className="flex flex-col items-center gap-3 px-6 py-14 text-center">
          <Inbox className="h-8 w-8 text-muted-foreground" aria-hidden="true" />
          <p className="font-medium text-foreground">{emptyMessage}</p>
          {emptyHint && (
            <p className="max-w-sm text-sm text-muted-foreground">{emptyHint}</p>
          )}
          {emptyAction}
        </div>
      )}

      <nav
        aria-label="Pagination"
        className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 border-t border-border text-sm text-muted-foreground"
      >
        <div aria-live="polite">
          Page <span className="text-foreground">{currentPage}</span> of{" "}
          <span className="text-foreground">{totalPages}</span>
          {Number.isFinite(total) && (
            <span className="ml-2">
              · <span className="text-foreground">{total}</span>{" "}
              {total === 1 ? "record" : "records"}
            </span>
          )}
        </div>

        <div className="flex gap-2">
          <Button
            label="Prev"
            size="sm"
            variant="outline"
            disabled={loading || currentPage <= 1}
            onClick={() => onPageChange?.(currentPage - 1)}
          />
          <Button
            label="Next"
            size="sm"
            variant="outline"
            disabled={loading || currentPage >= totalPages}
            onClick={() => onPageChange?.(currentPage + 1)}
          />
        </div>
      </nav>
    </div>
  );
};

export default DataTable;
