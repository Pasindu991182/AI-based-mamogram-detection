// ExBI-RADS Engine logomark — a teal aperture/target glyph.
// `light` renders for dark backgrounds (header/footer); default is for light bg.
export default function Brand({ size = 28, showText = true, subtitle = false, light = false }) {
  return (
    <div className="flex items-center gap-2.5">
      <span
        className={`grid place-items-center rounded-xl shadow-sm ${
          light
            ? "bg-white/15 text-white ring-1 ring-white/25"
            : "bg-brand-600 text-white ring-1 ring-brand-700/20"
        }`}
        style={{ width: size, height: size }}
        aria-hidden
      >
        <svg
          viewBox="0 0 24 24"
          width={size * 0.62}
          height={size * 0.62}
          fill="none"
          stroke="currentColor"
          strokeWidth="2.2"
          strokeLinecap="round"
        >
          <circle cx="12" cy="12" r="8.5" />
          <circle cx="12" cy="12" r="3.2" fill="currentColor" stroke="none" />
        </svg>
      </span>
      {showText && (
        <div className="leading-tight">
          <div
            className={`font-extrabold tracking-tight ${
              light ? "text-white" : "text-slate-900"
            }`}
          >
            ExBI-RADS{" "}
            <span className={light ? "text-brand-300" : "text-brand-600"}>
              Engine
            </span>
          </div>
          {subtitle && (
            <div
              className={`text-[11px] font-medium uppercase tracking-wider ${
                light ? "text-brand-200/80" : "text-slate-400"
              }`}
            >
              Explainable breast-cancer AI
            </div>
          )}
        </div>
      )}
    </div>
  );
}
