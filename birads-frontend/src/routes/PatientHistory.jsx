import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { FiArrowLeft, FiClock, FiInbox } from "react-icons/fi";
import { listCases } from "@/lib/api";

function biradsChip(code) {
  if (code == null) return "bg-slate-100 text-slate-500 border-slate-200";
  if (code >= 5) return "bg-red-100 text-red-700 border-red-300";
  if (code === 4) return "bg-orange-100 text-orange-700 border-orange-300";
  if (code === 3) return "bg-amber-100 text-amber-700 border-amber-300";
  return "bg-emerald-100 text-emerald-700 border-emerald-300";
}

export default function PatientHistory() {
  const { ref } = useParams();
  const navigate = useNavigate();
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    listCases(ref)
      .then(setCases)
      .catch(() => setCases([]))
      .finally(() => setLoading(false));
  }, [ref]);

  const latest = cases[0];
  const maxBirads = cases.reduce((m, c) => Math.max(m, c.birads_code ?? 0), 0);

  return (
    <div>
      <button
        onClick={() => navigate("/worklist")}
        className="mb-4 inline-flex items-center gap-1.5 text-sm font-semibold text-slate-500 transition hover:text-brand-700"
      >
        <FiArrowLeft /> Back to worklist
      </button>

      {/* Header */}
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-extrabold tracking-tight text-slate-900">
            <FiClock className="text-brand-600" /> Patient history
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            <span className="font-mono font-semibold text-slate-700">{ref}</span>
            {latest?.patient_age != null && ` · ${latest.patient_age}y`} ·{" "}
            {cases.length} stud{cases.length === 1 ? "y" : "ies"}
          </p>
        </div>
        {maxBirads >= 4 && (
          <span className="rounded-full border border-orange-300 bg-orange-50 px-3 py-1 text-xs font-bold text-orange-700">
            Highest BI-RADS: {maxBirads} — suspicious
          </span>
        )}
      </div>

      {/* Timeline */}
      <div className="mt-6 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="grid grid-cols-[1fr_0.7fr_0.9fr_1fr_1fr] gap-2 border-b border-slate-100 bg-slate-50 px-5 py-3 text-[11px] font-bold uppercase tracking-wide text-slate-400">
          <span>Date</span>
          <span>Views</span>
          <span>BI-RADS</span>
          <span>ER status</span>
          <span>Status</span>
        </div>

        {loading ? (
          <div className="px-5 py-16 text-center text-sm text-slate-400">Loading…</div>
        ) : cases.length === 0 ? (
          <div className="flex flex-col items-center gap-3 px-5 py-16 text-center">
            <FiInbox size={32} className="text-slate-300" />
            <p className="text-sm text-slate-500">No studies for this patient.</p>
          </div>
        ) : (
          cases.map((c) => (
            <div
              key={c.id}
              role="button"
              tabIndex={0}
              onClick={() => navigate(`/case/${c.id}`)}
              onKeyDown={(e) => e.key === "Enter" && navigate(`/case/${c.id}`)}
              className="grid cursor-pointer grid-cols-[1fr_0.7fr_0.9fr_1fr_1fr] items-center gap-2 border-b border-slate-50 px-5 py-3.5 text-sm transition last:border-0 hover:bg-brand-50/40"
            >
              <span className="font-mono text-xs text-slate-600">
                {new Date(c.created_at).toLocaleString()}
              </span>
              <span className="text-slate-500">{c.views ?? "—"}</span>
              <span>
                <span
                  className={`inline-flex min-w-7 justify-center rounded-md border px-2 py-0.5 font-mono text-xs font-bold ${biradsChip(
                    c.birads_code
                  )}`}
                >
                  {c.birads_code ?? "—"}
                </span>
              </span>
              <span className="font-mono text-xs text-slate-600">
                {c.er_result
                  ? `${c.er_result === "ER Positive" ? "ER+" : "ER−"} ${
                      c.er_probability_positive != null
                        ? Math.round(
                            (c.er_result === "ER Positive"
                              ? c.er_probability_positive
                              : 1 - c.er_probability_positive) * 100
                          ) + "%"
                        : ""
                    }`
                  : "—"}
              </span>
              <span className="font-medium text-slate-600">
                {c.report_finalized || c.status === "completed"
                  ? "Signed"
                  : c.status === "reported"
                    ? "Awaiting sign-off"
                    : c.status === "analyzed"
                      ? "Analyzed"
                      : "Draft"}
              </span>
            </div>
          ))
        )}
      </div>

      <p className="mt-3 text-xs text-slate-400">
        Chronological record of every study for this patient. Click a row to
        reopen it.
      </p>
    </div>
  );
}
