import { FiGithub, FiShield, FiCpu } from "react-icons/fi";
import Brand from "@/components/Brand";

const PIPELINE = [
  "Attention U-Net segmentation",
  "Radiomic feature extraction",
  "White-box BI-RADS scoring",
  "ER-status prediction",
  "Automated reporting",
  "Clinical RAG assistant",
];

const STACK = ["React", "FastAPI", "TensorFlow", "XGBoost", "LangChain"];

export default function Footer() {
  const year = new Date().getFullYear();
  return (
    <footer className="no-print mt-auto border-t border-brand-800 bg-brand-900 text-brand-100">
      <div className="mx-auto max-w-7xl px-6 py-12">
        <div className="grid gap-10 md:grid-cols-4">
          {/* Brand + mission */}
          <div className="md:col-span-2">
            {/* Brand inverted for the dark footer */}
            <div className="flex items-center gap-2.5">
              <span className="grid h-8 w-8 place-items-center rounded-xl bg-white/15 text-white ring-1 ring-white/20">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none"
                  stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
                  <circle cx="12" cy="12" r="8.5" />
                  <circle cx="12" cy="12" r="3.2" fill="currentColor" stroke="none" />
                </svg>
              </span>
              <span className="text-lg font-extrabold tracking-tight text-white">
                ExBI-RADS <span className="text-brand-300">Engine</span>
              </span>
            </div>
            <p className="mt-4 max-w-md text-sm leading-relaxed text-brand-200">
              An explainable, end-to-end breast-cancer decision-support system —
              from mammogram segmentation to BI-RADS scoring, ER-status
              prediction, automated reporting, and a guideline-grounded clinical
              assistant. Built to mirror a radiologist's reasoning, transparently.
            </p>
            <div className="mt-5 flex flex-wrap gap-2">
              {STACK.map((s) => (
                <span
                  key={s}
                  className="rounded-full bg-white/10 px-3 py-1 text-[11px] font-semibold text-brand-100 ring-1 ring-white/10"
                >
                  {s}
                </span>
              ))}
            </div>
          </div>

          {/* Pipeline */}
          <div>
            <h4 className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-brand-300">
              <FiCpu /> Pipeline
            </h4>
            <ul className="mt-4 space-y-2 text-sm text-brand-200">
              {PIPELINE.map((p) => (
                <li key={p} className="flex items-start gap-2">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-400" />
                  {p}
                </li>
              ))}
            </ul>
          </div>

          {/* Safety + project */}
          <div>
            <h4 className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-brand-300">
              <FiShield /> Clinical safety
            </h4>
            <p className="mt-4 text-sm leading-relaxed text-brand-200">
              A decision-support aid — <strong className="text-white">not</strong> an
              autonomous diagnostic device. Every output must be reviewed by a
              qualified clinician before any clinical decision.
            </p>
            <a
              href="https://github.com"
              target="_blank"
              rel="noreferrer"
              className="mt-5 inline-flex items-center gap-2 rounded-lg bg-white/10 px-3 py-2 text-sm font-semibold text-white ring-1 ring-white/10 transition hover:bg-white/15"
            >
              <FiGithub /> Project repository
            </a>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-10 flex flex-col items-center justify-between gap-3 border-t border-white/10 pt-6 text-xs text-brand-300 sm:flex-row">
          <p>© {year} ExBI-RADS Engine · Final-year research project.</p>
          <p className="text-center sm:text-right">
            For research &amp; educational use only — not for primary clinical
            diagnosis.
          </p>
        </div>
      </div>
    </footer>
  );
}
