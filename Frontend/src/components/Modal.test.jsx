/**
 * @vitest-environment jsdom
 */
import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Modal from "./Modal";

const open = (props = {}) =>
  render(
    <Modal title="Edit department" onClose={props.onClose ?? vi.fn()}>
      <input aria-label="Name" />
      <button type="button">Save</button>
    </Modal>,
  );

describe("Modal", () => {
  it("announces itself as a dialog with a name", () => {
    open();
    expect(screen.getByRole("dialog")).toHaveAccessibleName("Edit department");
    expect(screen.getByRole("dialog")).toHaveAttribute("aria-modal", "true");
  });

  it("moves focus into the dialog on open", () => {
    open();
    expect(screen.getByLabelText("Name")).toHaveFocus();
  });

  it("returns focus to whatever opened it", async () => {
    render(<button type="button">Add department</button>);
    const opener = screen.getByRole("button", { name: "Add department" });
    opener.focus();

    const { unmount } = open();
    unmount();

    expect(opener).toHaveFocus();
  });

  it("does not open with focus parked on the dismiss button", () => {
    open();
    expect(screen.getByRole("button", { name: "Close dialog" })).not.toHaveFocus();
  });

  it("traps Tab inside the dialog", async () => {
    open();
    const input = screen.getByLabelText("Name");
    const save = screen.getByRole("button", { name: "Save" });
    const close = screen.getByRole("button", { name: "Close dialog" });

    expect(input).toHaveFocus();
    await userEvent.tab();
    expect(save).toHaveFocus();

    await userEvent.tab();
    expect(close).toHaveFocus();
    await userEvent.tab();
    expect(input).toHaveFocus();
  });

  it("wraps backwards too", async () => {
    open();
    const close = screen.getByRole("button", { name: "Close dialog" });
    const save = screen.getByRole("button", { name: "Save" });

    close.focus();
    await userEvent.tab({ shift: true });
    expect(save).toHaveFocus();
  });

  it("closes on Escape", async () => {
    const onClose = vi.fn();
    open({ onClose });
    await userEvent.keyboard("{Escape}");
    expect(onClose).toHaveBeenCalled();
  });

  it("closes on a backdrop click but not on a click inside the panel", async () => {
    const onClose = vi.fn();
    open({ onClose });

    await userEvent.click(screen.getByRole("dialog"));
    expect(onClose).not.toHaveBeenCalled();

    await userEvent.click(screen.getByRole("dialog").parentElement);
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("stops the page behind it from scrolling, and restores that on close", () => {
    const { unmount } = open();
    expect(document.body.style.overflow).toBe("hidden");
    unmount();
    expect(document.body.style.overflow).not.toBe("hidden");
  });
});
