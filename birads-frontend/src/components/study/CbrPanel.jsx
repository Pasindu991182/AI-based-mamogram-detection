import { useState } from "react";
import {
  FiCheckCircle,
  FiAlertTriangle,
  FiActivity,
  FiLayers,
  FiShield,
  FiInfo,
  FiExternalLink,
} from "react-icons/fi";

export default function CbrPanel({ cbr, className = "mt-8", hideTitle = false }) {
  if (!cbr || !cbr.matches || cbr.matches.length === 0) {
    return null;
  }

  const { matches, biopsy_concordance, malignant_count, actionable_recommendation, clinical_rationale } =
    cbr;
  const isAllBenign = malignant_count === 0;
  const [selectedCase, setSelectedCase] = useState(null);

  return (
    <div className={`rounded-2xl border border-brand-200 bg-gradient-to-b from-brand-50/50 to-white p-5 sm:p-6 shadow-sm ${className}`}>
      {/* Top Header */}
      {!hideTitle ? (
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-brand-100 pb-4">
          <div className="flex items-center gap-2.5">
            <div className="grid h-9 w-9 place-items-center rounded-xl bg-brand-600 text-white shadow-sm shadow-brand-600/30">
              <FiLayers size={18} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-slate-900">
                  Case-Based Reasoning (CBR) · Historical Patient Twins
                </h3>
                <span className="rounded-full bg-brand-100 px-2.5 py-0.5 text-[10px] font-extrabold uppercase tracking-wider text-brand-700">
                  XAI Novelty
                </span>
              </div>
              <p className="text-xs text-slate-500">
                Retrieves the 3 most morphologically similar verified cases from historical biopsy database
              </p>
            </div>
          </div>

          {/* Biopsy Concordance Badge */}
          <div
            className={`flex items-center gap-2 rounded-xl px-3.5 py-1.5 text-xs font-bold ${
              isAllBenign
                ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                : "bg-rose-50 text-rose-700 border border-rose-200"
            }`}
          >
            {isAllBenign ? (
              <FiCheckCircle className="text-emerald-600" size={15} />
            ) : (
              <FiAlertTriangle className="text-rose-600" size={15} />
            )}
            <span>{biopsy_concordance}</span>
          </div>
        </div>
      ) : (
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-brand-100 pb-3">
          <div className="flex items-center gap-2">
            <span className="rounded-full bg-brand-100 px-2.5 py-0.5 text-[10px] font-extrabold uppercase tracking-wider text-brand-700">
              XAI Twin-Case Retrieval
            </span>
            <span className="text-xs text-slate-500">
              Corroborated by verified historical histopathology
            </span>
          </div>
          <div
            className={`flex items-center gap-2 rounded-xl px-3.5 py-1.5 text-xs font-bold ${
              isAllBenign
                ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                : "bg-rose-50 text-rose-700 border border-rose-200"
            }`}
          >
            {isAllBenign ? (
              <FiCheckCircle className="text-emerald-600" size={15} />
            ) : (
              <FiAlertTriangle className="text-rose-600" size={15} />
            )}
            <span>{biopsy_concordance}</span>
          </div>
        </div>
      )}

      {/* Actionable Clinical Recommendation Banner */}
      {actionable_recommendation && (
        <div className="my-4 rounded-xl border border-blue-200 bg-blue-50/70 p-3.5 text-xs">
          <div className="flex items-start gap-2.5">
            <div className="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-md bg-blue-600 text-white">
              <FiShield size={12} />
            </div>
            <div>
              <span className="font-bold text-blue-900">Actionable ACR Clinical Recommendation: </span>
              <span className="text-blue-800 leading-relaxed">{actionable_recommendation}</span>
              {clinical_rationale && (
                <p className="mt-1 text-[11px] text-blue-700/90 italic">
                  Rationale: {clinical_rationale}
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 3 Matched Historical Patient Twin Cards */}
      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {matches.map((item, idx) => {
          const isMal = item.is_malignant;
          const matchPct = item.similarity_percentage;
          const isSelected = selectedCase?.case_id === item.case_id;

          return (
            <div
              key={item.case_id || idx}
              onClick={() => setSelectedCase(isSelected ? null : item)}
              className={`group relative flex flex-col justify-between rounded-xl border bg-white p-4 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md cursor-pointer ${
                isSelected
                  ? "border-brand-500 ring-2 ring-brand-400/20"
                  : isMal
                  ? "border-rose-200 hover:border-rose-300"
                  : "border-slate-200 hover:border-brand-300"
              }`}
            >
              {/* Card Top: Case ID & Similarity Match */}
              <div>
                <div className="flex items-center justify-between gap-2 border-b border-slate-100 pb-2.5">
                  <div>
                    <span className="font-mono text-xs font-bold text-slate-800">
                      {item.case_id}
                    </span>
                    <span className="ml-1.5 text-[11px] text-slate-400">
                      Age {item.patient_age}F
                    </span>
                  </div>
                  <div
                    className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 font-mono text-[11px] font-black ${
                      matchPct >= 90
                        ? "bg-emerald-100 text-emerald-800"
                        : matchPct >= 80
                        ? "bg-brand-100 text-brand-800"
                        : "bg-amber-100 text-amber-800"
                    }`}
                  >
                    <FiActivity size={10} />
                    {matchPct}% Match
                  </div>
                </div>

                {/* Lesion Visual Precedent Thumbnail */}
                <div className="my-3 flex items-center gap-3">
                  <div
                    className="h-20 w-20 shrink-0 overflow-hidden rounded-lg border border-slate-200 bg-slate-900 shadow-inner"
                    dangerouslySetInnerHTML={{ __html: item.thumbnail_svg }}
                  />
                  <div className="min-w-0 flex-1">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                      Historical Study View
                    </div>
                    <div className="mt-0.5 text-xs font-bold text-slate-800">
                      {item.ground_truth_label}
                    </div>
                    <div className="mt-1 flex flex-wrap gap-1">
                      <span className="inline-block rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-semibold text-slate-600">
                        ER: {item.er_status}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Ground Truth Biopsy Result */}
                <div
                  className={`rounded-lg p-2.5 text-xs font-semibold ${
                    isMal
                      ? "bg-rose-50 text-rose-800 border border-rose-200/80"
                      : "bg-emerald-50 text-emerald-800 border border-emerald-200/80"
                  }`}
                >
                  <div className="flex items-center gap-1.5">
                    {isMal ? (
                      <FiAlertTriangle className="shrink-0 text-rose-600" size={13} />
                    ) : (
                      <FiCheckCircle className="shrink-0 text-emerald-600" size={13} />
                    )}
                    <span className="font-bold">Biopsy Proven Outcome:</span>
                  </div>
                  <p className="mt-1 text-[11px] font-medium leading-tight">
                    {item.biopsy_outcome}
                  </p>
                </div>

                {/* Morphology Highlights */}
                <div className="mt-2.5 text-[11px] text-slate-600">
                  <span className="font-semibold text-slate-700">Morphology: </span>
                  {item.key_morphology}
                </div>
              </div>

              {/* Action Taken */}
              <div className="mt-3 border-t border-slate-100 pt-2 text-[10px] text-slate-500">
                <span className="font-semibold text-slate-600">Outcome: </span>
                {item.clinical_action_taken}
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer Info Note */}
      <div className="mt-4 flex items-center justify-between text-[11px] text-slate-400">
        <span className="flex items-center gap-1">
          <FiInfo size={12} />
          Case-based reasoning retrieves nearest historical patient vectors by weighted radiomic Euclidean distance.
        </span>
        <span className="font-mono text-[10px] text-brand-600 font-medium">
          ACR BI-RADS Atlas Conformance
        </span>
      </div>
    </div>
  );
}
