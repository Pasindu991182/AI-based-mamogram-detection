const TAG = {
  warn: "bg-orange-50 text-orange-700 border-orange-200",
  high: "bg-red-50 text-red-700 border-red-200",
  ok: "bg-slate-50 text-slate-600 border-slate-200",
};

// Feature display metadata + qualitative interpretation of each value.
const FEATURES = [
  {
    key: "circularity",
    label: "Circularity",
    bar: (v) => v,
    fmt: (v) => v.toFixed(2),
    tag: (v) => (v < 0.5 ? ["irregular", "warn"] : ["rounded", "ok"]),
  },
  {
    key: "margin_integrity",
    label: "Margin integrity",
    bar: (v) => v,
    fmt: (v) => v.toFixed(2),
    tag: (v) =>
      v < 0.75 ? ["spiculated", "high"] : v >= 0.9 ? ["smooth", "ok"] : ["lobulated", "warn"],
  },
  {
    key: "orientation_index",
    label: "Orientation",
    bar: (v) => Math.min(v, 2) / 2,
    fmt: (v) => v.toFixed(2),
    tag: (v) => (v < 0.9 ? ["tall > wide", "warn"] : ["parallel", "ok"]),
  },
  {
    key: "max_diameter",
    label: "Diameter",
    unit: "px",
    bar: (v) => Math.min(v / 40, 1),
    fmt: (v) => v.toFixed(1),
    tag: () => ["→ ER step", "ok"],
  },
  {
    key: "contrast_ratio",
    label: "Contrast",
    bar: (v) => Math.min(v, 1),
    fmt: (v) => v.toFixed(2),
    tag: (v) => (v >= 0.5 ? ["high", "ok"] : ["low", "ok"]),
  },
  {
    key: "density_score",
    label: "Density",
    unit: "%",
    bar: (v) => Math.min(v / 100, 1),
    fmt: (v) => v.toFixed(0),
    tag: (v) => (v >= 50 ? ["dense", "ok"] : ["fatty", "ok"]),
  },
];

export default function FeaturesStep({ result }) {
  const wc = result.worst_case_radiomics;
  const byView = Object.fromEntries(
    result.analyzed_views
      .filter((v) => v.radiomic_features)
      .map((v) => [v.view.replace(" View", ""), v.radiomic_features])
  );

  if (!wc) {
    return (
      <p className="rounded-xl bg-slate-50 p-6 text-center text-sm italic text-slate-400">
        No lesion was detected on the analysed views — no radiomic features to
        measure.
      </p>
    );
  }

  return (
    <div>
      <div className="mb-4 flex items-baseline justify-between">
        <h3 className="text-base font-bold text-slate-800">
          6 radiomic features — worst-case of CC &amp; MLO
        </h3>
        <span className="font-mono text-[11px] text-slate-400">
          OpenCV · measured from fused mask
        </span>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {FEATURES.map((f) => {
          const v = wc[f.key];
          const [tagText, tagKind] = f.tag(v);
          const pct = Math.round(f.bar(v) * 100);
          return (
            <div
              key={f.key}
              className="rounded-xl border border-slate-200 bg-white p-4"
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-800">{f.label}</span>
                <span
                  className={`rounded-md border px-2 py-0.5 font-mono text-[11px] ${TAG[tagKind]}`}
                >
                  {tagText}
                </span>
              </div>
              <div className="mt-2 font-mono text-2xl font-bold text-slate-900">
                {f.fmt(v)}
                {f.unit && (
                  <span className="ml-1 text-sm font-normal text-slate-400">
                    {f.unit}
                  </span>
                )}
              </div>
              <div className="my-2 h-1.5 overflow-hidden rounded-full bg-slate-100">
                <div
                  className="h-full rounded-full bg-brand-500"
                  style={{ width: `${pct}%` }}
                />
              </div>
              <div className="font-mono text-[10px] text-slate-400">
                {byView.CC && `CC ${f.fmt(byView.CC[f.key])} · `}
                {byView.MLO && `MLO ${f.fmt(byView.MLO[f.key])}`}
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-5 inline-block rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 font-mono text-[11px] text-slate-500">
        feature vector → [
        {FEATURES.map((f) => f.fmt(wc[f.key])).join(", ")}]
      </div>
    </div>
  );
}
