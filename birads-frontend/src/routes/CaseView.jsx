import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  FiArrowLeft,
  FiEdit2,
  FiDownload,
  FiPrinter,
  FiCheckCircle,
  FiImage,
} from "react-icons/fi";
import { getCaseDetail } from "@/lib/api";

function biradsChip(code) {
  if (code == null) return "bg-slate-100 text-slate-500 border-slate-200";
  if (code >= 5) return "bg-red-100 text-red-700 border-red-300";
  if (code === 4) return "bg-orange-100 text-orange-700 border-orange-300";
  if (code === 3) return "bg-amber-100 text-amber-700 border-amber-300";
  return "bg-emerald-100 text-emerald-700 border-emerald-300";
}

function ImageCard({ label, url }) {
  return (
    <div>
      <div className="mb-1.5 text-[11px] font-bold uppercase tracking-wide text-slate-400">
        {label}
      </div>
      <div className="relative flex aspect-[3/4] w-full items-center justify-center overflow-hidden rounded-xl border-2 border-slate-200 bg-black">
        {url ? (
          <img src={url} alt={label} className="h-full w-full object-contain" />
        ) : (
          <div className="flex flex-col items-center gap-1.5 text-slate-500">
            <FiImage size={22} />
            <span className="text-xs italic">No image stored</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default function CaseView() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    setLoading(true);
    setError("");
    getCaseDetail(id)
      .then(setDetail)
      .catch(() => setError("Could not load this case. Is the backend running?"))
      .finally(() => setLoading(false));
  }, [id]);

  async function handleExport() {
    if (!detail) return;
    setExporting(true);
    try {
      const { exportReportPdf } = await import("@/lib/exportPdf");
      const a = detail.analysis;
      const er = detail.er_prediction;
      const document_ = {
        title: "Mammography Radiology Report",
        subtitle:
          "AI-Assisted Breast Cancer Decision Support System — Auto-generated report",
        meta: [
          { label: "Patient ID", value: detail.patient_ref || "—" },
          {
            label: "Study date",
            value: new Date(detail.created_at).toLocaleDateString(),
          },
          {
            label: "Age",
            value: detail.patient_age != null ? String(detail.patient_age) : "—",
          },
          { label: "Report type", value: "Auto-generated (system)" },
        ],
        features: a?.feature_rows ?? [],
        birads: {
          category: a?.birads_code != null ? `BI-RADS ${a.birads_code}` : "—",
          rationale: a?.birads_label ?? "",
          recommendation:
            a?.birads_code >= 4
              ? "Tissue biopsy is recommended."
              : "Routine screening / follow-up as clinically indicated.",
        },
        er: er?.er_result
          ? {
              er_result: er.er_result,
              probability_positive: er.probability_positive ?? 0,
              confidence: er.confidence ?? "—",
              inputs_summary: `Age ${er.age ?? "—"}, Tumor size ${er.tumor_size ?? "—"} mm, Grade ${er.histologic_grade ?? "—"}, Cellularity ${er.cellularity ?? "—"}, ${er.menopausal_state ?? "—"}-menopausal, ${er.histologic_subtype ?? "—"}, Lymph nodes positive: ${er.lymph_nodes_positive ?? "—"}`,
            }
          : null,
        impression: detail.report?.edited_text ?? detail.report?.generated_text ?? "",
      };
      exportReportPdf({
        document: document_,
        impression: document_.impression,
        generator: detail.report?.generator,
      });
    } finally {
      setExporting(false);
    }
  }

  if (loading) {
    return <div className="py-16 text-center text-sm text-slate-400">Loading case…</div>;
  }
  if (error || !detail) {
    return (
      <div className="rounded-lg border-l-4 border-red-500 bg-red-50 p-4 text-sm font-medium text-red-700">
        {error || "Case not found."}
      </div>
    );
  }

  const a = detail.analysis;
  const er = detail.er_prediction;
  const finalized = !!detail.report?.finalized_at;

  return (
    <div>
      {/* Header */}
      <div className="no-print mb-4 flex items-center justify-between">
        <button
          onClick={() => navigate("/worklist")}
          className="inline-flex items-center gap-1.5 text-sm font-semibold text-slate-500 transition hover:text-brand-700"
        >
          <FiArrowLeft /> Back to worklist
        </button>
        <button
          onClick={() => navigate(`/study?case=${detail.id}`)}
          className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
        >
          <FiEdit2 /> Continue / edit study
        </button>
      </div>

      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">
            {detail.patient_ref || `Case #${detail.id}`}
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            {detail.patient_age != null && `${detail.patient_age}y · `}
            {new Date(detail.created_at).toLocaleString()}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {a?.birads_code != null && (
            <span
              className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-sm font-bold ${biradsChip(a.birads_code)}`}
            >
              BI-RADS {a.birads_code}
            </span>
          )}
          {finalized && (
            <span className="inline-flex items-center gap-1.5 rounded-full border border-brand-300 bg-brand-50 px-3 py-1 text-sm font-bold text-brand-700">
              <FiCheckCircle /> Signed
            </span>
          )}
        </div>
      </div>

      {/* CC / MLO images */}
      <div className="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-sm font-bold text-slate-800">Original views</h2>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <ImageCard label="CC view" url={detail.cc_image_url} />
          <ImageCard label="MLO view" url={detail.mlo_image_url} />
          <ImageCard label="Attention overlay" url={a?.overlay_url} />
          <ImageCard label="Binary mask" url={a?.mask_url} />
        </div>
      </div>

      {/* Features + BI-RADS */}
      {a && (
        <div className="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-sm font-bold text-slate-800">
            Morphological features (worst-case CC/MLO)
          </h2>
          {a.feature_rows?.length > 0 ? (
            <table className="w-full overflow-hidden rounded-lg border border-slate-200 text-sm">
              <thead>
                <tr className="bg-slate-50 text-left text-[11px] uppercase tracking-wide text-slate-400">
                  <th className="px-3 py-2 font-bold">Feature</th>
                  <th className="px-3 py-2 font-bold">Value</th>
                  <th className="px-3 py-2 font-bold">Interpretation</th>
                </tr>
              </thead>
              <tbody>
                {a.feature_rows.map((r) => (
                  <tr key={r.feature} className="border-t border-slate-100">
                    <td className="px-3 py-2 font-semibold text-slate-700">{r.feature}</td>
                    <td className="px-3 py-2 font-mono text-slate-600">{r.value}</td>
                    <td className="px-3 py-2 text-slate-500">{r.interpretation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="text-sm italic text-slate-400">No morphological features recorded.</p>
          )}
        </div>
      )}

      {/* ER prediction */}
      {er?.er_result && (
        <div className="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-sm font-bold text-slate-800">ER status prediction</h2>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className="rounded-xl bg-slate-50 p-3">
              <p className="text-[11px] font-bold uppercase text-slate-400">Prediction</p>
              <p className="text-lg font-black text-slate-800">{er.er_result}</p>
            </div>
            <div className="rounded-xl bg-slate-50 p-3">
              <p className="text-[11px] font-bold uppercase text-slate-400">P(ER+)</p>
              <p className="text-lg font-black text-slate-800">
                {er.probability_positive != null
                  ? `${Math.round(er.probability_positive * 100)}%`
                  : "—"}
              </p>
            </div>
            <div className="rounded-xl bg-slate-50 p-3">
              <p className="text-[11px] font-bold uppercase text-slate-400">Confidence</p>
              <p className="text-lg font-black text-slate-800">{er.confidence ?? "—"}</p>
            </div>
            <div className="rounded-xl bg-slate-50 p-3">
              <p className="text-[11px] font-bold uppercase text-slate-400">Model</p>
              <p className="text-lg font-black text-slate-800">{er.model_version}</p>
            </div>
          </div>
        </div>
      )}

      {/* Report */}
      <div className="mt-6 rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="flex items-center justify-between border-b border-slate-100 px-6 py-4">
          <h2 className="text-sm font-bold text-slate-800">Saved report</h2>
          {detail.report && (
            <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-[10px] font-bold uppercase text-slate-500">
              {detail.report.generator}
            </span>
          )}
        </div>
        <div className="px-6 py-5">
          {detail.report ? (
            <p className="whitespace-pre-wrap font-serif text-sm leading-relaxed text-slate-800">
              {detail.report.edited_text ?? detail.report.generated_text}
            </p>
          ) : (
            <p className="text-sm italic text-slate-400">
              No report generated yet for this case.
            </p>
          )}
        </div>
        {detail.report && (
          <div className="no-print flex flex-wrap justify-end gap-2 border-t border-slate-100 px-6 py-3">
            <button
              onClick={() => window.print()}
              className="inline-flex items-center gap-2 rounded-lg border border-slate-300 px-3.5 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
            >
              <FiPrinter /> Print
            </button>
            <button
              onClick={handleExport}
              disabled={exporting}
              className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-b from-brand-500 to-brand-600 px-4 py-2 text-sm font-semibold text-white shadow-sm shadow-brand-600/30 transition hover:-translate-y-0.5 hover:shadow-md disabled:opacity-60"
            >
              <FiDownload /> {exporting ? "Preparing…" : "Export PDF"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
