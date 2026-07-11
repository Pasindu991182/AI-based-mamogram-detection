import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { FiArrowLeft, FiArrowRight, FiCheck, FiSave } from "react-icons/fi";
import {
  analyze,
  createCase,
  generateReport,
  getCase,
  predictER,
  updateReport,
} from "@/lib/api";
import Brand from "@/components/Brand";
import Stepper from "@/components/Stepper";
import UploadStep from "@/components/study/UploadStep";
import SegmentStep from "@/components/study/SegmentStep";
import FeaturesStep from "@/components/study/FeaturesStep";
import BiRadsStep from "@/components/study/BiRadsStep";
import ErStep from "@/components/study/ErStep";
import ReportStep from "@/components/study/ReportStep";

const STEPS = ["Upload", "Segment", "Features", "BI-RADS", "ER Status", "Report"];

const ER_DEFAULTS = {
  age: 54,
  tumor_size: 20,
  histologic_grade: 2,
  cellularity: "Moderate",
  menopausal_state: "Post",
  histologic_subtype: "Ductal/NST",
  lymph_nodes_positive: 0,
};

export default function Study() {
  const navigate = useNavigate();
  const [params] = useSearchParams();

  const [step, setStep] = useState(0);
  const [maxReached, setMaxReached] = useState(0);
  const [error, setError] = useState("");

  const [patient, setPatient] = useState({ ref: "", age: 54, sex: "F", clinic: "" });
  const [cc, setCc] = useState(null);
  const [mlo, setMlo] = useState(null);
  const [caseId, setCaseId] = useState(null);

  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);

  const [erForm, setErForm] = useState(ER_DEFAULTS);
  const [predicting, setPredicting] = useState(false);
  const [erResult, setErResult] = useState(null);

  const [generating, setGenerating] = useState(false);
  const [reportId, setReportId] = useState(null);
  const [reportText, setReportText] = useState("");
  const [reportDoc, setReportDoc] = useState(null);
  const [reportGen, setReportGen] = useState("");
  const [saving, setSaving] = useState(false);
  const [finalizing, setFinalizing] = useState(false);
  const [finalized, setFinalized] = useState(false);

  // Prefill from an existing worklist case (patient + caseId only).
  useEffect(() => {
    const id = params.get("case");
    if (!id) return;
    getCase(id)
      .then((c) => {
        setCaseId(c.id);
        setPatient((p) => ({
          ...p,
          ref: c.patient_ref || p.ref,
          age: c.patient_age ?? p.age,
        }));
      })
      .catch(() => {});
  }, [params]);

  // Once analysis exists, seed the ER form with the worst-case tumour size.
  useEffect(() => {
    if (!result) return;
    const d = result.worst_case_radiomics?.max_diameter;
    setErForm((f) => ({
      ...f,
      age: patient.age,
      tumor_size: d != null ? Number(d.toFixed(1)) : f.tumor_size,
    }));
  }, [result, patient.age]);

  const go = (n) => {
    setError("");
    setStep(n);
    setMaxReached((m) => Math.max(m, n));
  };

  const predictedClass = result?.analyzed_views?.some(
    (v) => v.predicted_class === "Mass Detected"
  )
    ? "Mass Detected"
    : "No Mass Detected";

  async function runAnalysis() {
    if (!cc && !mlo) return setError("Upload at least one view (CC or MLO).");
    setError("");
    setAnalyzing(true);
    try {
      let cid = caseId;
      if (cid == null) {
        const c = await createCase({
          patient_ref: patient.ref,
          patient_age: patient.age,
        });
        cid = c.id;
        setCaseId(cid);
      }
      const res = await analyze(patient.age, cc, mlo, cid);
      setResult(res);
      go(1);
    } catch {
      setError("Analysis failed. Check that the backend is running.");
    } finally {
      setAnalyzing(false);
    }
  }

  async function runPredict() {
    setError("");
    setPredicting(true);
    try {
      setErResult(await predictER({ ...erForm, case_id: caseId }));
    } catch {
      setError("ER prediction failed.");
    } finally {
      setPredicting(false);
    }
  }

  async function runReport() {
    if (!result) return;
    setError("");
    setGenerating(true);
    try {
      const views = result.analyzed_views
        ?.map((v) => v.view.replace(" View", ""))
        .join(" + ");
      const rep = await generateReport({
        case_id: caseId,
        features: result.worst_case_radiomics ?? {
          circularity: 0,
          margin_integrity: 1,
          orientation_index: 1,
          max_diameter: 0,
          contrast_ratio: 0,
          density_score: 0,
        },
        birads_code: result.overall_birads_code ?? 2,
        patient_age: patient.age,
        predicted_class: predictedClass,
        patient: {
          patient_ref: patient.ref,
          age: patient.age,
          sex: patient.sex,
          laterality: patient.laterality || "",
          menopausal_state:
            erForm.menopausal_state === "Post"
              ? "Post-menopausal"
              : "Pre-menopausal",
          referring_facility: patient.clinic || "",
        },
        er: erResult
          ? {
              er_result: erResult.er_result,
              probability_positive: erResult.probability_positive,
              confidence: erResult.confidence,
              inputs_summary: `Age ${erForm.age}, Tumor size ${erForm.tumor_size} mm, Histologic grade ${erForm.histologic_grade}, Cellularity ${erForm.cellularity}, ${erForm.menopausal_state}-menopausal, ${erForm.histologic_subtype}, Lymph nodes positive: ${erForm.lymph_nodes_positive}`,
            }
          : null,
      });
      setReportId(rep.id ?? null);
      setReportDoc(rep.document ?? null);
      setReportGen(rep.generator ?? "");
      setReportText(rep.impression ?? rep.edited_text ?? rep.generated_text);
      go(5);
    } catch {
      setError("Report generation failed.");
    } finally {
      setGenerating(false);
    }
  }

  async function saveReport(finalize) {
    if (reportId == null) return;
    finalize ? setFinalizing(true) : setSaving(true);
    try {
      await updateReport(reportId, reportText, finalize);
      if (finalize) setFinalized(true);
    } catch {
      setError("Saving the report failed.");
    } finally {
      finalize ? setFinalizing(false) : setSaving(false);
    }
  }

  // Primary footer action per step.
  const primary = [
    { label: "Run segmentation", onClick: runAnalysis, busy: analyzing, disabled: !cc && !mlo },
    { label: "Measure features", onClick: () => go(2) },
    { label: "Classify BI-RADS", onClick: () => go(3) },
    { label: "Predict ER status", onClick: () => go(4) },
    { label: "Generate report", onClick: runReport, busy: generating, disabled: !erResult },
    null,
  ][step];

  return (
    <div>
      <div className="no-print mb-4 flex items-center justify-between">
        <button
          onClick={() => navigate("/worklist")}
          className="inline-flex items-center gap-1.5 text-sm font-semibold text-slate-500 hover:text-slate-800"
        >
          <FiArrowLeft /> Worklist
        </button>
        {result && (
          <span className="font-mono text-xs text-slate-400">
            {patient.ref || "unsaved"} · {patient.age}
            {patient.sex}
          </span>
        )}
      </div>

      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        {/* Card header + stepper */}
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 bg-slate-50/60 px-5 py-3">
          <Brand size={26} subtitle={false} />
          <span className="font-mono text-xs text-slate-400">
            {patient.ref ? `${patient.ref} · ${patient.age}${patient.sex}` : "New study"}
          </span>
        </div>
        <div className="no-print border-b border-slate-100 px-5 py-3">
          <Stepper steps={STEPS} current={step} maxReached={maxReached} onStep={go} />
        </div>

        {/* Body */}
        <div className="p-5 sm:p-6">
          {error && (
            <div className="mb-5 rounded-lg border-l-4 border-red-500 bg-red-50 p-3 text-sm font-medium text-red-700">
              {error}
            </div>
          )}

          {step === 0 && (
            <UploadStep
              patient={patient}
              setPatient={setPatient}
              cc={cc}
              setCc={setCc}
              mlo={mlo}
              setMlo={setMlo}
            />
          )}
          {step === 1 && result && (
            <SegmentStep
              result={result}
              files={{ "CC View": cc, "MLO View": mlo }}
            />
          )}
          {step === 2 && result && <FeaturesStep result={result} />}
          {step === 3 && result && <BiRadsStep result={result} />}
          {step === 4 && (
            <ErStep
              form={erForm}
              setForm={setErForm}
              result={erResult}
              onPredict={runPredict}
              predicting={predicting}
              autoTumor={result?.worst_case_radiomics?.max_diameter != null}
            />
          )}
          {step === 5 && (
            <ReportStep
              document={reportDoc}
              generator={reportGen}
              value={reportText}
              onChange={setReportText}
              onSave={() => saveReport(false)}
              saving={saving}
              onFinalize={() => saveReport(true)}
              finalizing={finalizing}
              finalized={finalized}
            />
          )}
        </div>

        {/* Footer */}
        {primary && (
          <div className="no-print flex items-center justify-between border-t border-slate-100 bg-slate-50/60 px-5 py-3">
            <button
              onClick={() => step > 0 && go(step - 1)}
              disabled={step === 0}
              className="inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-semibold text-slate-500 transition hover:bg-slate-100 disabled:invisible"
            >
              <FiArrowLeft /> Back
            </button>
            <button
              onClick={primary.onClick}
              disabled={primary.busy || primary.disabled}
              className="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700 disabled:opacity-50"
            >
              {primary.busy ? "Working…" : primary.label}
              {!primary.busy && <FiArrowRight />}
            </button>
          </div>
        )}

        {step === 5 && (
          <div className="no-print flex items-center justify-between border-t border-slate-100 bg-slate-50/60 px-5 py-3">
            <button
              onClick={() => go(4)}
              className="inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-semibold text-slate-500 transition hover:bg-slate-100"
            >
              <FiArrowLeft /> Back
            </button>
            <div className="flex items-center gap-2">
              <button
                onClick={() => saveReport(false)}
                disabled={saving || finalized || reportId == null}
                className="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700 disabled:opacity-50"
              >
                <FiSave />
                {finalized ? "Report saved" : saving ? "Saving…" : "Save report"}
              </button>
              <button
                onClick={() => navigate("/worklist")}
                className="inline-flex items-center gap-2 rounded-xl border border-slate-300 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-white"
              >
                <FiCheck /> Done — back to worklist
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
