const Modal = ({ title, onClose, children }) => {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      onClick={onClose}
    >
      <div
        className="
          relative w-full max-w-lg
          bg-background text-foreground
          border border-border
          rounded-xl p-6
          shadow-lg
        "
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">{title}</h2>

          <button
            type="button"
            onClick={onClose}
            className="
              text-muted-foreground
              hover:text-foreground
              text-xl font-bold
              transition
            "
          >
            ✕
          </button>
        </div>

        {children}
      </div>
    </div>
  );
};

export default Modal;
