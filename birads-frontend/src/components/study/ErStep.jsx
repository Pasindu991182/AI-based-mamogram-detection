import { FiActivity, FiFlag } from "react-icons/fi";

function Field({ label, accent, children }) {
  return (
    <label className="block">
      <span
        className={`mb-1 block text-[11px] font-bold uppercase tracking-wide ${
          accent ? "text-brand-600" : "text-slate-500"
        }`}
      >
        {label}
      </span>
      {children}
    </label>
  );
}

const inputCls =
  "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium focus:border-brand-500 focus:outline-none";

const DIR = {
  "ER+": "text-brand-700 bg-brand-50 border-brand-200",
  "ER-": "text-red-600 bg-red-50 border-red-200",
  neutral: "text-slate-400 bg-slate-50 border-slate-200",
};

export default function ErStep({
  form,
  setForm,
  result,
  onPredict,
  predicting,
  autoTumor,
}) {
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));
  const positive = result?.er_result === "ER Positive";
  const pPos = result ? Math.round(result.probability_positive * 100) : 0;

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {/* Inputs */}
      <div>
        <h3 className="mb-4 text-base font-bold text-slate-800">
          7 routine clinical inputs
        </h3>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Age">
            <input
              type="number"
              className={inputCls}
              value={form.age}
              onChange={(e) => set("age", Number(e.target.value))}
            />
          </Field>
          <Field label={autoTumor ? "Tumor size · auto" : "Tumor size (mm)"} accent={autoTumor}>
            <input
              type="number"
              className={`${inputCls} ${autoTumor ? "border-brand-400 bg-brand-50" : ""}`}
              value={form.tumor_size}
              onChange={(e) => set("tumor_size", Number(e.target.value))}
            />
          </Field>
          <Field label="Histologic grade">
            <select
              className={inputCls}
              value={form.histologic_grade}
              onChange={(e) => set("histologic_grade", Number(e.target.value))}
            >
              {[1, 2, 3].map((g) => (
                <option key={g} value={g}>
                  Grade {g}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Cellularity">
            <select
              className={inputCls}
              value={form.cellularity}
              onChange={(e) => set("cellularity", e.target.value)}
            >
              {["Low", "Moderate", "High"].map((c) => (
                <option key={c}>{c}</option>
              ))}
            </select>
          </Field>
          <Field label="Menopausal state">
            <select
              className={inputCls}
              value={form.menopausal_state}
              onChange={(e) => set("menopausal_state", e.target.value)}
            >
              <option value="Pre">Pre</option>
              <option value="Post">Post</option>
            </select>
          </Field>
          <Field label="Histologic subtype">
            <select
              className={inputCls}
              value={form.histologic_subtype}
              onChange={(e) => set("histologic_subtype", e.target.value)}
            >
              {/* values MUST match the backend SUBTYPE_MAP / trained LabelEncoder */}
              {[
                ["Ductal/NST", "Ductal / NST"],
                ["Lobular", "Lobular"],
                ["Mixed", "Mixed"],
                ["Mucinous", "Mucinous"],
                ["Medullary", "Medullary"],
                ["Metaplastic", "Metaplastic"],
                ["Tubular/ cribriform", "Tubular / cribriform"],
                ["Other", "Other"],
              ].map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </Field>
          <div className="col-span-2">
            <Field label="Lymph nodes positive">
              <input
                type="number"
                className={inputCls}
                value={form.lymph_nodes_positive}
                onChange={(e) =>
                  set("lymph_nodes_positive", Number(e.target.value))
                }
              />
            </Field>
          </div>
        </div>
        <p className="mt-4 rounded-lg bg-brand-50 px-3 py-2 text-xs text-brand-700">
          No IHC needed — all 7 inputs come from a basic hospital workup.
        </p>
        <button
          onClick={onPredict}
          disabled={predicting}
          className="mt-4 inline-flex items-center gap-2 rounded-xl bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:opacity-50"
        >
          <FiActivity /> {predicting ? "Predicting…" : "Predict ER status"}
        </button>
      </div>

      {/* Result */}
      <div>
        {!result ? (
          <div className="grid h-full min-h-72 place-items-center rounded-2xl border-2 border-dashed border-slate-200 text-sm text-slate-400">
            Prediction will appear here
          </div>
        ) : (
          <div className="space-y-4">
            <div
              className={`rounded-2xl border p-5 text-center shadow-sm ${
                positive
                  ? "border-brand-200 bg-brand-50"
                  : "border-orange-200 bg-orange-50"
              }`}
            >
              <div className="text-[11px] font-bold uppercase tracking-wide text-slate-400">
                Prediction
              </div>
              <div
                className={`my-1 text-3xl font-extrabold ${
                  positive ? "text-brand-700" : "text-orange-700"
                }`}
              >
                {positive ? "ER POSITIVE" : "ER NEGATIVE"}
              </div>
              <span className="inline-flex rounded-md bg-slate-900 px-2.5 py-0.5 font-mono text-[11px] text-white">
                confidence: {result.confidence?.toUpperCase()}
              </span>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-4">
              <div className="flex justify-between font-mono text-[11px] text-slate-500">
                <span>ER+ {pPos}%</span>
                <span>{100 - pPos}% ER−</span>
              </div>
              <div className="mt-1.5 flex h-4 overflow-hidden rounded-md border border-slate-200">
                <div className="bg-brand-500" style={{ width: `${pPos}%` }} />
                <div className="bg-slate-200" style={{ width: `${100 - pPos}%` }} />
              </div>
              <p className="mt-3 font-mono text-[10px] text-slate-400">
                model: {result.model_version}
              </p>

              {result.contributions?.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {result.contributions.map((c) => (
                    <span
                      key={c.feature}
                      className={`rounded-md border px-2 py-0.5 text-[11px] ${
                        DIR[c.direction] ?? DIR.neutral
                      }`}
                    >
                      {c.feature}: {c.value}
                      {c.direction !== "neutral" && ` (${c.direction})`}
                    </span>
                  ))}
                </div>
              )}
            </div>

            <div className="rounded-2xl border-2 border-dashed border-brand-300 bg-brand-50/60 p-4">
              <div className="flex items-center gap-2 font-bold text-brand-700">
                <FiFlag /> Treatment signal
              </div>
              <p className="mt-1 text-sm text-slate-600">
                {result.treatment_signal || result.recommendation}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
