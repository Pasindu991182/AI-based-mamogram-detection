const MEANING = {
  2: ["Benign", "benign finding", "text-emerald-600", "bg-emerald-50"],
  3: ["Probably benign", "short-interval follow-up", "text-amber-600", "bg-amber-50"],
  4: ["Suspicious", "high suspicion of malignancy", "text-orange-600", "bg-orange-50"],
  5: ["Highly suggestive", "highly suggestive of malignancy", "text-red-600", "bg-red-50"],
};

const RULE_DOT = {
  high: "bg-red-500",
  warn: "bg-orange-500",
  info: "bg-brand-500",
};

export default function BiRadsStep({ result }) {
  const code = result.overall_birads_code ?? 4;
  const [name, sub, color, bg] = MEANING[code] ?? MEANING[4];
  const ex = result.explanation ?? { rules: [], feature_importance: [] };

  return (
    <div className="grid gap-6 lg:grid-cols-[300px_1fr]">
      {/* Category */}
      <div>
        <div
          className={`rounded-2xl border border-slate-200 p-6 text-center shadow-sm ${bg}`}
        >
          <div className="text-[11px] font-bold uppercase tracking-wide text-slate-400">
            Assigned category
          </div>
          <div className={`my-1 text-6xl font-extrabold leading-none ${color}`}>
            {code}
          </div>
          <div className={`text-lg font-bold ${color}`}>{name}</div>
          <div className="mt-1 text-xs text-slate-500">{sub}</div>
        </div>

        {/* Scale 2..5 */}
        <div className="mt-4 flex overflow-hidden rounded-lg border border-slate-200">
          {[2, 3, 4, 5].map((n) => (
            <div
              key={n}
              className={`flex-1 py-2 text-center font-mono text-sm font-bold ${
                n === code
                  ? "bg-slate-900 text-white"
                  : "bg-white text-slate-400"
              }`}
            >
              {n}
            </div>
          ))}
        </div>
        <div className="mt-1.5 flex justify-between font-mono text-[10px] text-slate-400">
          <span>benign</span>
          <span>malignant</span>
        </div>
        {result.overall_birads_label && (
          <p className="mt-4 text-xs text-slate-500">
            Model band: {result.overall_birads_label}
          </p>
        )}
      </div>

      {/* Explanation */}
      <div className="rounded-2xl border border-brand-200 bg-brand-50/40 p-5">
        <h3 className="text-base font-bold text-slate-800">
          {ex.headline || `Why BI-RADS ${code}?`}
        </h3>
        <p className="font-mono text-[11px] text-brand-600">
          {ex.model || "white-box classifier · ACR BI-RADS Atlas"}
        </p>

        <div className="mt-4 space-y-2">
          {ex.rules.length === 0 && (
            <p className="text-sm italic text-slate-400">
              No morphology rules fired — category driven by deep features.
            </p>
          )}
          {ex.rules.map((r, i) => (
            <div
              key={i}
              className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white px-3 py-2.5"
            >
              <span
                className={`h-2 w-2 shrink-0 rounded-full ${
                  RULE_DOT[r.severity] ?? RULE_DOT.info
                }`}
              />
              <span className="text-sm text-slate-700">
                <span className="font-mono text-xs text-brand-600">RULE </span>
                <b>
                  {r.feature} {r.condition}
                </b>{" "}
                → {r.interpretation}
              </span>
            </div>
          ))}
        </div>

        {ex.feature_importance.length > 0 && (
          <>
            <h4 className="mt-5 mb-2 text-sm font-bold text-slate-700">
              Feature importance
            </h4>
            <div className="space-y-1.5">
              {ex.feature_importance.map((fi) => (
                <div key={fi.feature} className="flex items-center gap-3">
                  <span className="w-28 font-mono text-[11px] text-slate-500">
                    {fi.feature}
                  </span>
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-white">
                    <div
                      className="h-full rounded-full bg-brand-500"
                      style={{ width: `${Math.round(fi.weight * 100)}%` }}
                    />
                  </div>
                  <span className="w-9 text-right font-mono text-[11px] text-slate-500">
                    {fi.weight.toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
