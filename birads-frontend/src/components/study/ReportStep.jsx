import { useState } from "react";
import { FiCheckCircle, FiCpu, FiDownload, FiPrinter, FiSave } from "react-icons/fi";

function SectionTitle({ n, children }) {
  return (
    <h3 className="mb-2 mt-6 flex items-center gap-2 text-sm font-bold text-slate-800">
      <span className="grid h-5 w-5 place-items-center rounded-md bg-brand-100 text-[11px] font-black text-brand-700">
        {n}
      </span>
      {children}
    </h3>
  );
}

export default function ReportStep({
  document: doc,
  generator,
  value,
  onChange,
  onSave,
  saving,
  onFinalize,
  finalizing,
  finalized,
}) {
  const isNlp = (generator || "").startsWith("nlp");
  const [exporting, setExporting] = useState(false);

  async function handleExport() {
    setExporting(true);
    try {
      // Lazy-load jsPDF only when needed (keeps the main bundle small).
      const { exportReportPdf } = await import("@/lib/exportPdf");
      exportReportPdf({ document: doc, impression: value, generator });
    } finally {
      setExporting(false);
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_240px]">
      {/* ============ The document ============ */}
      <div id="report-doc" className="rounded-xl border border-slate-200 bg-white shadow-sm">
        {/* Letterhead */}
        <div className="border-b-2 border-brand-600 px-8 py-6">
          <div className="text-center">
            <h2 className="text-lg font-black uppercase tracking-wide text-slate-900">
              {doc?.title ?? "Mammography Radiology Report"}
            </h2>
            <p className="mt-1 text-xs text-slate-500">
              {doc?.subtitle ??
                "AI-Assisted Breast Cancer Decision Support System — Auto-generated report"}
            </p>
          </div>
        </div>

        <div className="px-8 py-6">
          {/* Metadata grid */}
          {doc?.meta?.length > 0 && (
            <div className="grid grid-cols-2 gap-x-8 gap-y-2.5 rounded-lg bg-slate-50 p-4 text-sm sm:grid-cols-2">
              {doc.meta.map((m) => (
                <div key={m.label} className="flex justify-between gap-3 border-b border-slate-100 pb-1.5">
                  <span className="text-slate-400">{m.label}</span>
                  <span className="text-right font-semibold text-slate-700">
                    {m.value}
                  </span>
                </div>
              ))}
            </div>
          )}

          {/* 1. Segmentation */}
          {doc?.segmentation && (
            <>
              <SectionTitle n={1}>Segmentation · Tier 1 — Attention U-Net</SectionTitle>
              <p className="text-sm leading-relaxed text-slate-600">{doc.segmentation}</p>
            </>
          )}

          {/* 2. Morphological features */}
          {doc?.features?.length > 0 && (
            <>
              <SectionTitle n={2}>
                Morphological Feature Extraction · Tier 2 (worst-case CC/MLO)
              </SectionTitle>
              <table className="w-full overflow-hidden rounded-lg border border-slate-200 text-sm">
                <thead>
                  <tr className="bg-slate-50 text-left text-[11px] uppercase tracking-wide text-slate-400">
                    <th className="px-3 py-2 font-bold">Feature</th>
                    <th className="px-3 py-2 font-bold">Measured value</th>
                    <th className="px-3 py-2 font-bold">Interpretation</th>
                  </tr>
                </thead>
                <tbody>
                  {doc.features.map((r) => (
                    <tr key={r.feature} className="border-t border-slate-100">
                      <td className="px-3 py-2 font-semibold text-slate-700">
                        {r.feature}
                      </td>
                      <td className="px-3 py-2 font-mono text-slate-600">{r.value}</td>
                      <td className="px-3 py-2 text-slate-500">{r.interpretation}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}

          {/* 3. BI-RADS */}
          {doc?.birads && (
            <>
              <SectionTitle n={3}>
                BI-RADS Classification · Tier 3 — Atlas-driven rule engine
              </SectionTitle>
              <p className="text-sm font-bold text-slate-800">
                Assigned category: {doc.birads.category}
              </p>
              <p className="mt-1 text-sm leading-relaxed text-slate-600">
                {doc.birads.rationale}
              </p>
              <p className="mt-1 text-sm text-slate-600">
                <span className="font-semibold">Recommendation:</span>{" "}
                {doc.birads.recommendation}
              </p>
            </>
          )}

          {/* 4. ER status */}
          {doc?.er && (
            <>
              <SectionTitle n={4}>ER Status Prediction · Tier 4 — ensemble model</SectionTitle>
              <table className="w-full overflow-hidden rounded-lg border border-slate-200 text-sm">
                <tbody>
                  {[
                    ["Prediction", doc.er.er_result],
                    ["Probability (ER+)", `${Math.round(doc.er.probability_positive * 100)}%`],
                    ["Confidence level", doc.er.confidence],
                    ["Inputs used", doc.er.inputs_summary],
                  ].map(([k, v]) => (
                    <tr key={k} className="border-t border-slate-100 first:border-0">
                      <td className="w-40 bg-slate-50 px-3 py-2 font-semibold text-slate-600">
                        {k}
                      </td>
                      <td className="px-3 py-2 text-slate-700">{v}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}

          {/* 5. Impression (editable NLP narrative) */}
          <SectionTitle n={5}>
            Impression
            <span
              className={`ml-1 inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide ${
                isNlp
                  ? "bg-brand-100 text-brand-700"
                  : "bg-slate-100 text-slate-500"
              }`}
            >
              <FiCpu size={11} /> {isNlp ? "NLP-generated" : "template"}
            </span>
          </SectionTitle>
          <textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            rows={6}
            disabled={finalized}
            className="w-full resize-y rounded-lg border border-slate-200 bg-slate-50/40 p-4 font-serif text-sm leading-relaxed text-slate-800 focus:border-brand-500 focus:bg-white focus:outline-none disabled:opacity-70 print:border-0 print:bg-transparent print:p-0"
          />

          <p className="mt-4 border-t border-dashed border-slate-200 pt-3 text-[10px] leading-relaxed text-slate-400">
            Auto-drafted from Tier 1–4 outputs; the Impression is generated by a
            natural-language model. Decision-support aid — radiologist sign-off
            required. Not for primary clinical diagnosis.
          </p>
        </div>

        {/* Actions */}
        <div className="no-print flex flex-wrap justify-end gap-2 border-t border-slate-100 px-6 py-3">
          <button
            onClick={() => window.print()}
            className="group inline-flex items-center gap-2 rounded-lg border border-slate-300 px-3.5 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
          >
            <FiPrinter className="transition-transform group-hover:scale-110" />
            Print
          </button>
          {!finalized && (
            <button
              onClick={onSave}
              disabled={saving}
              className="inline-flex items-center gap-2 rounded-lg border border-slate-300 px-3.5 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-50"
            >
              <FiSave /> {saving ? "Saving…" : "Save draft"}
            </button>
          )}
          <button
            onClick={handleExport}
            disabled={exporting}
            className="group inline-flex items-center gap-2 rounded-lg bg-gradient-to-b from-brand-500 to-brand-600 px-4 py-2 text-sm font-semibold text-white shadow-sm shadow-brand-600/30 transition hover:-translate-y-0.5 hover:shadow-md disabled:opacity-60"
          >
            <FiDownload className="transition-transform group-hover:translate-y-0.5" />
            {exporting ? "Preparing…" : "Export PDF"}
          </button>
        </div>
      </div>

      {/* ============ Sidebar ============ */}
      <div className="no-print space-y-4">
        <div className="rounded-xl border border-brand-200 bg-brand-50 p-4">
          <div className="flex items-center gap-2 text-brand-700">
            <FiCpu />
            <span className="text-sm font-bold">
              {isNlp ? "NLP report engine" : "Template engine"}
            </span>
          </div>
          <p className="mt-2 text-xs leading-relaxed text-brand-800/80">
            {isNlp
              ? `The Impression is written by a natural-language model (${generator}) from the structured Tier 1–4 findings.`
              : "The Impression uses a deterministic template. Add an OpenAI key to enable NLP generation."}
          </p>
        </div>

        <div
          className={`rounded-xl border p-4 ${
            finalized ? "border-brand-300 bg-brand-50" : "border-slate-200 bg-white"
          }`}
        >
          <div className="flex items-center gap-2">
            <FiCheckCircle className={finalized ? "text-brand-600" : "text-slate-300"} />
            <span className="text-sm font-semibold text-slate-700">
              {finalized ? "Signed off" : "Radiologist sign-off"}
            </span>
          </div>
          {!finalized ? (
            <button
              onClick={onFinalize}
              disabled={finalizing}
              className="mt-3 w-full rounded-lg bg-brand-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:opacity-50"
            >
              {finalizing ? "Signing…" : "Sign & finalize"}
            </button>
          ) : (
            <p className="mt-2 text-xs text-slate-500">
              Report finalized and locked. It now appears as “Signed” in the
              worklist.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
