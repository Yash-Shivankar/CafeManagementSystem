/**
 * @vitest-environment jsdom
 */
import { describe, expect, it, vi } from "vitest";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import DataTable from "./DataTable";

const columns = [
  { key: "name", label: "Name" },
  { key: "amount", label: "Amount", render: (value) => `INR ${value}` },
];

const rows = [
  { id: 7, name: "Kitchen", amount: 120 },
  { id: 9, name: "Counter", amount: 240 },
];

const renderTable = (props = {}) =>
  render(<DataTable data={rows} columns={columns} {...props} />);

describe("DataTable", () => {
  it("renders a header per column plus Actions when the row is actionable", () => {
    renderTable({ onEdit: vi.fn() });

    const table = screen.getByRole("table");
    const headers = within(table).getAllByRole("columnheader");
    expect(headers.map((h) => h.textContent)).toEqual(["Name", "Amount", "Actions"]);
  });

  it("omits the Actions column when there is nothing to do to a row", () => {
    renderTable();
    const headers = within(screen.getByRole("table")).getAllByRole("columnheader");
    expect(headers).toHaveLength(2);
  });

  it("uses a column's render function for its cells", () => {
    renderTable();
    expect(screen.getAllByText("INR 120").length).toBeGreaterThan(0);
  });

  it("keys rows by their id, not their position", () => {
    const { rerender } = renderTable();
    const before = screen.getByRole("table").querySelectorAll("tbody tr");
    const firstCellBefore = before[0].querySelector("td");

    rerender(<DataTable data={[...rows].reverse()} columns={columns} />);

    const after = screen.getByRole("table").querySelectorAll("tbody tr");

    expect(after[1].querySelector("td")).toBe(firstCellBefore);
  });

  it("keeps the table frame while loading instead of replacing it", () => {
    renderTable({ loading: true });
    expect(screen.getByRole("table")).toBeInTheDocument();
    expect(screen.getAllByRole("columnheader").length).toBeGreaterThan(0);
    expect(screen.queryByText("Kitchen")).not.toBeInTheDocument();
  });

  it("explains an empty result instead of saying 'No data found'", () => {
    render(
      <DataTable
        data={[]}
        columns={columns}
        emptyMessage="No departments yet"
        emptyHint="Add one to get started."
      />,
    );
    expect(screen.getByText("No departments yet")).toBeInTheDocument();
    expect(screen.getByText("Add one to get started.")).toBeInTheDocument();
  });

  it("does not show the empty state while the first page is still loading", () => {
    render(<DataTable data={[]} columns={columns} loading emptyMessage="Nothing" />);
    expect(screen.queryByText("Nothing")).not.toBeInTheDocument();
  });

  it("passes the whole row to onEdit and onDelete", async () => {
    const onEdit = vi.fn();
    const onDelete = vi.fn();
    renderTable({ onEdit, onDelete });

    await userEvent.click(screen.getAllByRole("button", { name: "Edit" })[0]);
    expect(onEdit).toHaveBeenCalledWith(rows[0]);

    await userEvent.click(screen.getAllByRole("button", { name: "Delete" })[0]);
    expect(onDelete).toHaveBeenCalledWith(rows[0]);
  });

  describe("pagination", () => {
    it("disables Prev on the first page and Next on the last", () => {
      const { rerender } = renderTable({
        pagination: { currentPage: 1, totalPages: 3 },
      });
      expect(screen.getByRole("button", { name: "Prev" })).toBeDisabled();
      expect(screen.getByRole("button", { name: "Next" })).not.toBeDisabled();

      rerender(
        <DataTable
          data={rows}
          columns={columns}
          pagination={{ currentPage: 3, totalPages: 3 }}
        />,
      );
      expect(screen.getByRole("button", { name: "Next" })).toBeDisabled();
    });

    it("cannot page while a page is in flight", () => {
      renderTable({ loading: true, pagination: { currentPage: 2, totalPages: 3 } });
      expect(screen.getByRole("button", { name: "Next" })).toBeDisabled();
    });

    it("reports the total record count when the API gives one", () => {
      renderTable({ pagination: { currentPage: 1, totalPages: 3, total: 24 } });
      expect(screen.getByText("24")).toBeInTheDocument();
    });

    it("asks for the next page number", async () => {
      const onPageChange = vi.fn();
      renderTable({ pagination: { currentPage: 2, totalPages: 5 }, onPageChange });
      await userEvent.click(screen.getByRole("button", { name: "Next" }));
      expect(onPageChange).toHaveBeenCalledWith(3);
    });
  });
});
