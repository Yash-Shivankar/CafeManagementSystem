/**
 * @vitest-environment jsdom
 */
import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import FilterBar from "./FilterBar";

const filters = [
  { name: "search", label: "Search", type: "text", placeholder: "Name" },
  {
    name: "status",
    label: "Status",
    type: "select",
    options: [
      { value: "active", label: "Active" },
      { value: "inactive", label: "Inactive" },
    ],
  },
  { name: "from", label: "From", type: "date" },
];

const setup = (props = {}) => {
  const onChange = vi.fn();
  const onApply = vi.fn();
  const onReset = vi.fn();
  render(
    <FilterBar
      filters={filters}
      values={{}}
      onChange={onChange}
      onApply={onApply}
      onReset={onReset}
      {...props}
    />,
  );
  return { onChange, onApply, onReset };
};

describe("FilterBar", () => {
  it("renders one labelled control per declared filter", () => {
    setup();
    expect(screen.getByText("Search")).toBeInTheDocument();
    expect(screen.getByText("Status")).toBeInTheDocument();
    expect(screen.getByText("From")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Name")).toBeInTheDocument();
  });

  it("offers 'All' as the unset option on a select, plus each choice", () => {
    setup();
    const options = screen.getAllByRole("option").map((o) => o.textContent);
    expect(options).toEqual(["All", "Active", "Inactive"]);
  });

  it("reports each change by filter name", async () => {
    const { onChange } = setup();
    await userEvent.type(screen.getByPlaceholderText("Name"), "k");
    expect(onChange).toHaveBeenCalledWith("search", "k");

    await userEvent.selectOptions(screen.getByRole("combobox"), "inactive");
    expect(onChange).toHaveBeenCalledWith("status", "inactive");
  });

  it("is a controlled component — it shows the values it is given", () => {
    render(
      <FilterBar
        filters={filters}
        values={{ search: "Kitchen", status: "active" }}
        onChange={vi.fn()}
      />,
    );
    expect(screen.getByPlaceholderText("Name")).toHaveValue("Kitchen");
    expect(screen.getByRole("combobox")).toHaveValue("active");
  });

  it("applies and resets on demand", async () => {
    const { onApply, onReset } = setup();
    await userEvent.click(screen.getByRole("button", { name: "Apply" }));
    expect(onApply).toHaveBeenCalled();
    await userEvent.click(screen.getByRole("button", { name: "Reset" }));
    expect(onReset).toHaveBeenCalled();
  });

  it("hides the action buttons when the caller handles filtering itself", () => {
    render(<FilterBar filters={filters} values={{}} onChange={vi.fn()} />);
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("ignores a filter type it does not know rather than crashing the page", () => {
    render(
      <FilterBar
        filters={[...filters, { name: "mystery", label: "Mystery", type: "wat" }]}
        values={{}}
        onChange={vi.fn()}
      />,
    );
    expect(screen.queryByText("Mystery")).not.toBeInTheDocument();
    expect(screen.getByText("Search")).toBeInTheDocument();
  });
});
