import { FiCheck } from "react-icons/fi";

// Horizontal 6-step progress indicator for the diagnostic pipeline.
export default function Stepper({ steps, current, maxReached = 0, onStep }) {
  return (
    <div className="flex flex-wrap items-center gap-y-2">
      {steps.map((label, i) => {
        const done = i < current;
        const active = i === current;
        const reachable = i <= maxReached;
        return (
          <div key={label} className="flex items-center">
            <button
              type="button"
              disabled={!reachable}
              onClick={() => reachable && onStep?.(i)}
              className={`flex items-center gap-2 rounded-lg border-2 px-3 py-1.5 text-sm font-semibold transition ${
                active
                  ? "border-brand-600 bg-brand-600 text-white shadow-sm"
                  : done
                    ? "border-brand-200 bg-brand-50 text-brand-700 hover:bg-brand-100"
                    : "border-slate-200 bg-white text-slate-400"
              } ${reachable ? "cursor-pointer" : "cursor-not-allowed"}`}
            >
              <span
                className={`grid h-5 w-5 place-items-center rounded-full text-[11px] font-bold ${
                  active
                    ? "bg-white/25 text-white"
                    : done
                      ? "bg-brand-600 text-white"
                      : "bg-slate-100 text-slate-400"
                }`}
              >
                {done ? <FiCheck size={12} /> : i + 1}
              </span>
              {label}
            </button>
            {i < steps.length - 1 && (
              <span className="mx-1.5 text-slate-300">›</span>
            )}
          </div>
        );
      })}
    </div>
  );
}
