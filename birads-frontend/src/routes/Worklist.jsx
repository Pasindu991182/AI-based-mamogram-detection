import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  FiPlus,
  FiSearch,
  FiInbox,
  FiRefreshCw,
  FiX,
  FiClock,
  FiEdit2,
  FiTrash2,
  FiAlertTriangle,
  FiEye,
} from "react-icons/fi";
import { listCases, updateCase, deleteCase } from "@/lib/api";
import Button from "@/components/Button";
import Modal from "@/components/Modal";

function biradsChip(code) {
  if (code == null) return "bg-slate-100 text-slate-500 border-slate-200";
  if (code >= 5) return "bg-red-100 text-red-700 border-red-300";
  if (code === 4) return "bg-orange-100 text-orange-700 border-orange-300";
  if (code === 3) return "bg-amber-100 text-amber-700 border-amber-300";
  return "bg-emerald-100 text-emerald-700 border-emerald-300";
}

// Normalised status key used for both the badge and the status filter.
function statusKey(c) {
  if (c.report_finalized || c.status === "completed") return "signed";
  if (c.status === "reported") return "awaiting";
  if (c.status === "analyzed") return "analyzed";
  return "draft";
}

const STATUS_META = {
  signed: ["Signed", "text-brand-700"],
  awaiting: ["Awaiting sign-off", "text-orange-600"],
  analyzed: ["Analyzed", "text-slate-600"],
  draft: ["Draft", "text-slate-400"],
};

const selectCls =
  "rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-600 shadow-sm outline-none transition hover:bg-slate-50 focus:border-brand-400 cursor-pointer";

export default function Worklist() {
  const navigate = useNavigate();
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [q, setQ] = useState("");
  const [birads, setBirads] = useState("all"); // all | 2 | 3 | 4 | 5 | suspicious
  const [er, setEr] = useState("all"); // all | pos | neg
  const [status, setStatus] = useState("all"); // all | signed | awaiting | analyzed | draft

  const filtersActive =
    q !== "" || birads !== "all" || er !== "all" || status !== "all";

  function clearFilters() {
    setQ("");
    setBirads("all");
    setEr("all");
    setStatus("all");
  }

  // Edit / delete dialog state
  const [editing, setEditing] = useState(null); // case being edited
  const [editForm, setEditForm] = useState({ patient_ref: "", patient_age: "" });
  const [deleting, setDeleting] = useState(null); // case being deleted
  const [busy, setBusy] = useState(false);

  function openEdit(c) {
    setEditForm({ patient_ref: c.patient_ref ?? "", patient_age: c.patient_age ?? "" });
    setEditing(c);
  }

  async function saveEdit() {
    setBusy(true);
    try {
      await updateCase(editing.id, {
        patient_ref: editForm.patient_ref,
        patient_age: editForm.patient_age === "" ? null : Number(editForm.patient_age),
      });
      setEditing(null);
      await load();
    } catch {
      setError("Could not save changes.");
    } finally {
      setBusy(false);
    }
  }

  async function confirmDelete() {
    setBusy(true);
    try {
      await deleteCase(deleting.id);
      setDeleting(null);
      await load();
    } catch {
      setError("Could not delete the study.");
    } finally {
      setBusy(false);
    }
  }

  async function load() {
    setLoading(true);
    setError("");
    try {
      setCases(await listCases());
    } catch {
      setError("Could not load the worklist. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const rows = useMemo(() => {
    return cases.filter((c) => {
      // BI-RADS
      if (birads === "suspicious" && (c.birads_code ?? 0) < 4) return false;
      if (["1", "2", "3", "4", "5"].includes(birads) && String(c.birads_code) !== birads)
        return false;
      // ER status
      if (er !== "all") {
        const isPos = c.er_result === "ER Positive";
        if (er === "pos" && !isPos) return false;
        if (er === "neg" && (isPos || !c.er_result)) return false;
      }
      // Study status
      if (status !== "all" && statusKey(c) !== status) return false;
      // Search
      if (q) {
        const hay = `${c.patient_ref} ${c.id}`.toLowerCase();
        if (!hay.includes(q.toLowerCase())) return false;
      }
      return true;
    });
  }, [cases, q, birads, er, status]);

  return (
    <div>
      {/* Header */}
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">
            Worklist
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Patient studies signed to you · {cases.length} total
          </p>
        </div>
        <Button as="link" to="/study" icon={FiPlus}>
          New study
        </Button>
      </div>

      {/* Toolbar */}
      <div className="mt-5 flex flex-wrap items-center gap-3">
        <div className="flex min-w-55 flex-1 items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 shadow-sm">
          <FiSearch className="text-slate-400" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search patient ID / reference"
            className="w-full bg-transparent text-sm outline-none placeholder:text-slate-400"
          />
        </div>

        <select
          value={birads}
          onChange={(e) => setBirads(e.target.value)}
          className={selectCls}
          title="Filter by BI-RADS category"
        >
          <option value="all">All BI-RADS</option>
          <option value="suspicious">BI-RADS 4 &amp; 5 (suspicious)</option>
          <option value="1">BI-RADS 1</option>
          <option value="2">BI-RADS 2</option>
          <option value="3">BI-RADS 3</option>
          <option value="4">BI-RADS 4</option>
          <option value="5">BI-RADS 5</option>
        </select>

        <select
          value={er}
          onChange={(e) => setEr(e.target.value)}
          className={selectCls}
          title="Filter by ER status"
        >
          <option value="all">All ER status</option>
          <option value="pos">ER positive</option>
          <option value="neg">ER negative</option>
        </select>

        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className={selectCls}
          title="Filter by study status"
        >
          <option value="all">All statuses</option>
          <option value="signed">Signed</option>
          <option value="awaiting">Awaiting sign-off</option>
          <option value="analyzed">Analyzed</option>
          <option value="draft">Draft</option>
        </select>

        {filtersActive && (
          <button
            onClick={clearFilters}
            className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-500 transition hover:bg-red-50 hover:text-red-600"
            title="Clear all filters"
          >
            <FiX /> Clear
          </button>
        )}

        <button
          onClick={load}
          className="grid h-9 w-9 place-items-center rounded-xl border border-slate-200 bg-white text-slate-500 transition hover:bg-slate-50"
          title="Refresh"
        >
          <FiRefreshCw className={loading ? "animate-spin" : ""} />
        </button>
      </div>

      {/* Result count */}
      {!loading && (
        <p className="mt-3 text-xs font-medium text-slate-400">
          Showing {rows.length} of {cases.length} studies
          {filtersActive && " (filtered)"}
        </p>
      )}

      {error && (
        <div className="mt-4 rounded-lg border-l-4 border-red-500 bg-red-50 p-3 text-sm font-medium text-red-700">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="mt-5 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="grid grid-cols-[1.6fr_1fr_0.7fr_0.8fr_1fr_1fr_auto] gap-2 border-b border-slate-100 bg-slate-50 px-5 py-3 text-[11px] font-bold uppercase tracking-wide text-slate-400">
          <span>Patient</span>
          <span>Date</span>
          <span>Views</span>
          <span>BI-RADS</span>
          <span>ER status</span>
          <span>Status</span>
          <span className="text-right">Actions</span>
        </div>

        {loading ? (
          <div className="px-5 py-16 text-center text-sm text-slate-400">
            Loading worklist…
          </div>
        ) : rows.length === 0 ? (
          <div className="flex flex-col items-center gap-3 px-5 py-16 text-center">
            <FiInbox size={32} className="text-slate-300" />
            <p className="text-sm text-slate-500">
              {cases.length === 0
                ? "No studies yet. Start your first study."
                : "No studies match your filters."}
            </p>
            {cases.length === 0 && (
              <Button as="link" to="/study" size="sm" icon={FiPlus}>
                New study
              </Button>
            )}
          </div>
        ) : (
          rows.map((c) => {
            const [label, cls] = STATUS_META[statusKey(c)];
            return (
              <div
                key={c.id}
                role="button"
                tabIndex={0}
                onClick={() => navigate(`/study?case=${c.id}`)}
                onKeyDown={(e) =>
                  e.key === "Enter" && navigate(`/study?case=${c.id}`)
                }
                className="grid w-full cursor-pointer grid-cols-[1.6fr_1fr_0.7fr_0.8fr_1fr_1fr_auto] items-center gap-2 border-b border-slate-50 px-5 py-3.5 text-left text-sm transition last:border-0 hover:bg-brand-50/40"
              >
                <span className="font-semibold text-slate-800">
                  {c.patient_ref || `Case #${c.id}`}
                  {c.patient_age != null && (
                    <span className="font-normal text-slate-400">
                      {" "}
                      · {c.patient_age}y
                    </span>
                  )}
                </span>
                <span className="font-mono text-xs text-slate-500">
                  {new Date(c.created_at).toLocaleDateString()}
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
                <span className={`font-medium ${cls}`}>{label}</span>

                {/* Row actions — stopPropagation so they don't open the study */}
                <span
                  className="flex items-center justify-end gap-1"
                  onClick={(e) => e.stopPropagation()}
                >
                  <button
                    title="View report & images"
                    onClick={() => navigate(`/case/${c.id}`)}
                    className="grid h-8 w-8 place-items-center rounded-lg text-slate-400 transition hover:bg-brand-50 hover:text-brand-700"
                  >
                    <FiEye size={15} />
                  </button>
                  {c.patient_ref && (
                    <button
                      title="Patient history"
                      onClick={() =>
                        navigate(`/patient/${encodeURIComponent(c.patient_ref)}`)
                      }
                      className="grid h-8 w-8 place-items-center rounded-lg text-slate-400 transition hover:bg-brand-50 hover:text-brand-700"
                    >
                      <FiClock size={15} />
                    </button>
                  )}
                  <button
                    title="Edit patient"
                    onClick={() => openEdit(c)}
                    className="grid h-8 w-8 place-items-center rounded-lg text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
                  >
                    <FiEdit2 size={15} />
                  </button>
                  <button
                    title="Delete study"
                    onClick={() => setDeleting(c)}
                    className="grid h-8 w-8 place-items-center rounded-lg text-slate-400 transition hover:bg-red-50 hover:text-red-600"
                  >
                    <FiTrash2 size={15} />
                  </button>
                </span>
              </div>
            );
          })
        )}
      </div>

      <p className="mt-3 text-xs text-slate-400">
        Rural-clinic use: filter BI-RADS 4/5 to refer suspicious cases up the
        chain.
      </p>

      {/* Edit patient modal */}
      <Modal open={!!editing} onClose={() => setEditing(null)} title="Edit patient details">
        <div className="space-y-4">
          <label className="block">
            <span className="mb-1 block text-[11px] font-bold uppercase tracking-wide text-slate-500">
              Patient ID / reference
            </span>
            <input
              value={editForm.patient_ref}
              onChange={(e) =>
                setEditForm((f) => ({ ...f, patient_ref: e.target.value }))
              }
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium focus:border-brand-500 focus:outline-none"
              placeholder="PT-00428"
            />
          </label>
          <label className="block">
            <span className="mb-1 block text-[11px] font-bold uppercase tracking-wide text-slate-500">
              Age
            </span>
            <input
              type="number"
              value={editForm.patient_age}
              onChange={(e) =>
                setEditForm((f) => ({ ...f, patient_age: e.target.value }))
              }
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium focus:border-brand-500 focus:outline-none"
            />
          </label>
          <div className="flex justify-end gap-2 pt-2">
            <button
              onClick={() => setEditing(null)}
              className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              onClick={saveEdit}
              disabled={busy}
              className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-50"
            >
              {busy ? "Saving…" : "Save changes"}
            </button>
          </div>
        </div>
      </Modal>

      {/* Delete confirmation modal */}
      <Modal open={!!deleting} onClose={() => setDeleting(null)} title="Delete study">
        <div className="flex items-start gap-3">
          <span className="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-red-100 text-red-600">
            <FiAlertTriangle />
          </span>
          <div className="text-sm text-slate-600">
            Delete{" "}
            <strong className="text-slate-800">
              {deleting?.patient_ref || `Case #${deleting?.id}`}
            </strong>
            ? This permanently removes its segmentation, features, BI-RADS,
            report and ER prediction. This cannot be undone.
          </div>
        </div>
        <div className="mt-5 flex justify-end gap-2">
          <button
            onClick={() => setDeleting(null)}
            className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-50"
          >
            Cancel
          </button>
          <button
            onClick={confirmDelete}
            disabled={busy}
            className="inline-flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-50"
          >
            <FiTrash2 /> {busy ? "Deleting…" : "Delete"}
          </button>
        </div>
      </Modal>
    </div>
  );
}
