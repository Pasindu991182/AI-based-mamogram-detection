import { useRef } from "react";
import { FiUploadCloud, FiCheckCircle } from "react-icons/fi";

function FileDrop({ label, file, onChange }) {
  const inputRef = useRef(null);
  const url = file ? URL.createObjectURL(file) : null;
  return (
    <button
      type="button"
      onClick={() => inputRef.current?.click()}
      className={`relative flex h-56 w-full flex-col items-center justify-center gap-2 overflow-hidden rounded-xl border-2 p-4 text-center transition ${
        file
          ? "border-brand-500 bg-slate-900"
          : "border-dashed border-slate-300 bg-slate-50 hover:border-brand-400 hover:bg-brand-50/40"
      }`}
    >
      {file ? (
        <>
          <img
            src={url}
            alt={label}
            className="absolute inset-0 h-full w-full object-contain p-2"
          />
          <span className="absolute bottom-2 left-1/2 -translate-x-1/2 rounded-md bg-black/60 px-2 py-1 text-xs font-medium text-white">
            <FiCheckCircle className="mr-1 inline" />
            {label} · {file.name.slice(0, 18)}
          </span>
        </>
      ) : (
        <>
          <FiUploadCloud size={28} className="text-slate-400" />
          <span className="font-semibold text-slate-700">Drop {label}</span>
          <span className="text-xs text-slate-400">PNG / JPG / DICOM-PNG</span>
        </>
      )}
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(e) => onChange(e.target.files?.[0] ?? null)}
      />
    </button>
  );
}

function Field({ label, hint, children }) {
  return (
    <label className="block">
      <span className="mb-1 block text-[11px] font-bold uppercase tracking-wide text-slate-500">
        {label}
      </span>
      {children}
      {hint && <span className="mt-1 block text-xs text-slate-400">{hint}</span>}
    </label>
  );
}

const inputCls =
  "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium focus:border-brand-500 focus:outline-none";

export default function UploadStep({ patient, setPatient, cc, setCc, mlo, setMlo }) {
  const set = (k, v) => setPatient((p) => ({ ...p, [k]: v }));

  return (
    <div className="grid gap-8 lg:grid-cols-[320px_1fr]">
      {/* Patient details */}
      <div>
        <h3 className="mb-4 text-base font-bold text-slate-800">
          Patient details
        </h3>
        <div className="space-y-3">
          <Field label="Patient ID / reference" hint="Fixed PT-00 prefix — enter the number only.">
            <div className="flex w-full items-stretch overflow-hidden rounded-lg border border-slate-300 bg-white focus-within:border-brand-500">
              {/* Locked, non-editable prefix */}
              <span className="flex shrink-0 select-none items-center whitespace-nowrap border-r border-slate-200 bg-slate-50 px-3 text-sm font-bold tracking-wide text-slate-500">
                PT-00
              </span>
              <input
                className="w-full bg-transparent px-3 py-2 text-sm font-medium tabular-nums outline-none"
                value={patient.ref?.startsWith("PT-00") ? patient.ref.slice(5) : ""}
                onChange={(e) => {
                  const digits = e.target.value.replace(/\D/g, "").slice(0, 6);
                  set("ref", `PT-00${digits}`);
                }}
                inputMode="numeric"
                placeholder="428"
                aria-label="Patient number after PT-00 prefix"
              />
            </div>
          </Field>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Age">
              <input
                type="number"
                className={inputCls}
                value={patient.age}
                onChange={(e) => set("age", Number(e.target.value))}
              />
            </Field>
            <Field label="Sex">
              <select
                className={inputCls}
                value={patient.sex}
                onChange={(e) => set("sex", e.target.value)}
              >
                <option>F</option>
                <option>M</option>
              </select>
            </Field>
          </div>
          <Field label="Referring clinic">
            <input
              className={inputCls}
              value={patient.clinic}
              onChange={(e) => set("clinic", e.target.value)}
              placeholder="Select clinic"
            />
          </Field>
        </div>
        <p className="mt-4 rounded-lg bg-brand-50 px-3 py-2 text-xs text-brand-700">
          Age &amp; tumour size carry into the ER-status step automatically.
        </p>
      </div>

      {/* Upload */}
      <div>
        <h3 className="mb-4 text-base font-bold text-slate-800">
          Upload both views
        </h3>
        <div className="grid gap-4 sm:grid-cols-2">
          <FileDrop label="CC view" file={cc} onChange={setCc} />
          <FileDrop label="MLO view" file={mlo} onChange={setMlo} />
        </div>
        <p className="mt-3 text-xs text-slate-400">
          At least one view is required. Both CC + MLO give worst-case feature
          fusion.
        </p>
      </div>
    </div>
  );
}
