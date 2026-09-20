/**
 * @vitest-environment jsdom
 */
import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import DynamicForm from "./DynamicForm";

const fields = [
  { name: "name", label: "Name", type: "text", required: true },
  { name: "capacity", label: "Capacity", type: "number" },
  {
    name: "status",
    label: "Status",
    type: "select",
    options: [
      { value: "free", label: "Free" },
      { value: "seated", label: "Seated" },
    ],
  },
];

describe("DynamicForm", () => {
  it("submits only the declared fields, never the rest of the row", async () => {
    const onSubmit = vi.fn();
    render(
      <DynamicForm
        fields={fields}
        initialValues={{
          id: 12,
          name: "Window seat",
          capacity: 4,
          status: "free",
          created_at: "2026-01-01T00:00:00Z",
          created_by_user: { id: 1, email: "owner@cafe.com" },
        }}
        onSubmit={onSubmit}
      />,
    );

    await userEvent.click(screen.getByRole("button", { name: "Save" }));

    expect(onSubmit).toHaveBeenCalledTimes(1);
    expect(Object.keys(onSubmit.mock.calls[0][0]).sort()).toEqual([
      "capacity",
      "name",
      "status",
    ]);
  });

  it("ties every label to its control, so clicking the label focuses it", async () => {
    render(<DynamicForm fields={fields} onSubmit={vi.fn()} />);

    const input = screen.getByLabelText(/Name/);
    await userEvent.click(screen.getByText("Name"));
    expect(input).toHaveFocus();
  });

  it("sends what the user typed", async () => {
    const onSubmit = vi.fn();
    render(<DynamicForm fields={fields} onSubmit={onSubmit} />);

    await userEvent.type(screen.getByLabelText(/Name/), "Corner table");
    await userEvent.selectOptions(screen.getByLabelText("Status"), "seated");
    await userEvent.click(screen.getByRole("button", { name: "Save" }));

    expect(onSubmit).toHaveBeenCalledWith({ name: "Corner table", status: "seated" });
  });

  it("shows a field error next to the field and marks it invalid", () => {
    render(
      <DynamicForm
        fields={fields}
        onSubmit={vi.fn()}
        errors={{ name: "A table with that name already exists" }}
      />,
    );

    const input = screen.getByLabelText(/Name/);
    expect(input).toHaveAttribute("aria-invalid", "true");
    expect(screen.getByRole("alert")).toHaveTextContent(
      "A table with that name already exists",
    );
    expect(input).toHaveAccessibleDescription(
      "A table with that name already exists",
    );
  });

  it("cannot be submitted twice while the first save is in flight", async () => {
    const onSubmit = vi.fn();
    render(<DynamicForm fields={fields} onSubmit={onSubmit} submitting />);

    const button = screen.getByRole("button");
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute("aria-busy", "true");

    await userEvent.click(button);
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("offers a way out when the caller provides one", async () => {
    const onCancel = vi.fn();
    render(<DynamicForm fields={fields} onSubmit={vi.fn()} onCancel={onCancel} />);
    await userEvent.click(screen.getByRole("button", { name: "Cancel" }));
    expect(onCancel).toHaveBeenCalled();
  });
});
