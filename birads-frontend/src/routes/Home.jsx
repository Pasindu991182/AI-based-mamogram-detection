import { FiCheckCircle, FiImage, FiMail, FiShield } from "react-icons/fi";
import { useAuth } from "@/hooks/useAuth";
import Reveal from "@/components/Reveal";
import BrowserMock from "@/components/BrowserMock";
import worklistShot from "@/assets/Screenshot 2026-07-07 at 21.13.28.png";
import biradsShot from "@/assets/Screenshot 2026-07-07 at 20.57.55.png";
import erShot from "@/assets/Screenshot 2026-07-07 at 20.58.03.png";

const PIPELINE = [
  { n: 1, title: "Upload", desc: "CC + MLO mammogram views with patient details." },
  { n: 2, title: "Segment", desc: "Attention U-Net isolates the lesion with a binary mask." },
  { n: 3, title: "Features", desc: "Six radiomic features measured from the fused mask." },
  { n: 4, title: "BI-RADS", desc: "White-box classifier assigns a category, rules shown." },
  { n: 5, title: "ER Status", desc: "ER+/ER− predicted from 7 routine clinical inputs." },
  { n: 6, title: "Report", desc: "Auto-generated report, signed off by the radiologist." },
];

const SAFETY_BADGES = ["Radiologist sign-off required", "Full audit trail", "Guideline-grounded"];

/** Full-bleed section: breaks out of the app's centered <main> to span the viewport. */
function FullBleed({ id, className = "", children }) {
  return (
    <div id={id} className={`relative left-1/2 w-screen -translate-x-1/2 ${className}`}>
      <div className="mx-auto max-w-7xl px-4 sm:px-6">{children}</div>
    </div>
  );
}

function Eyebrow({ children, dark, className = "" }) {
  return (
    <span
      className={`block text-xs font-bold uppercase tracking-widest ${
        dark ? "text-brand-300" : "text-brand-600"
      } ${className}`}
    >
      {children}
    </span>
  );
}

export default function Home() {
  const { user } = useAuth();

  return (
    <div className="-mt-6 sm:-mt-8">
      {/* ================= Hero ================= */}
      <FullBleed className="overflow-hidden bg-gradient-to-br from-brand-900 via-brand-800 to-brand-900 py-20 text-white">
        <div className="animate-float-slow pointer-events-none absolute -left-20 top-0 h-72 w-72 rounded-full bg-brand-400/20 blur-3xl" />
        <div className="animate-float-slower pointer-events-none absolute -right-16 top-24 h-80 w-80 rounded-full bg-brand-300/15 blur-3xl" />

        <div className="relative mx-auto max-w-3xl text-center">
          <Reveal>
            <span className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1 text-[11px] font-bold uppercase tracking-wider text-brand-100 backdrop-blur">
              <span className="h-1.5 w-1.5 rounded-full bg-brand-300" />
              Decision support · Mammography
            </span>
            <h1 className="mt-5 text-4xl font-extrabold leading-tight tracking-tight sm:text-5xl">
              Explainable breast-cancer decision support, end to end.
            </h1>
            <p className="mx-auto mt-5 max-w-xl text-lg leading-relaxed text-brand-100/90">
              From mammogram segmentation to white-box BI-RADS scoring,
              ER-status prediction and an auto-generated radiology report —
              every output traceable to the rules that produced it.
            </p>
            <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
              <a
                href="#contact"
                className="group inline-flex items-center gap-2 rounded-xl bg-white px-5 py-3 text-sm font-bold text-brand-800 shadow-lg shadow-black/10 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-xl"
              >
                Contact us
                <span className="transition-transform group-hover:translate-x-1">→</span>
              </a>
              <a
                href="#pipeline"
                className="inline-flex items-center gap-2 rounded-xl border border-white/25 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10"
              >
                See the pipeline
              </a>
            </div>
          </Reveal>
        </div>

        <Reveal delay={150} className="relative mx-auto mt-14 max-w-5xl">
          <BrowserMock url="exbi-rads.app / worklist" image={worklistShot} alt="ExBI-RADS worklist" />
        </Reveal>
      </FullBleed>

      {/* ================= Pipeline ================= */}
      <section id="pipeline" className="py-24">
        <Reveal className="mx-auto max-w-2xl text-center">
          <Eyebrow>The pipeline</Eyebrow>
          <h2 className="mt-2 text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl">
            Six steps. One signed report.
          </h2>
        </Reveal>

        <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {PIPELINE.map((p, i) => (
            <Reveal key={p.n} delay={i * 80}>
              <div className="group h-full rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-brand-300 hover:shadow-lg">
                <span className="grid h-10 w-10 place-items-center rounded-full bg-brand-600 text-sm font-black text-white transition-transform duration-300 group-hover:scale-110">
                  {p.n}
                </span>
                <h3 className="mt-4 text-base font-bold text-slate-900">{p.title}</h3>
                <p className="mt-1.5 text-sm leading-relaxed text-slate-500">{p.desc}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ================= White-box scoring spotlight ================= */}
      <section className="py-16">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <Reveal>
            <Eyebrow>White-box scoring</Eyebrow>
            <h2 className="mt-2 text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl">
              BI-RADS you can interrogate
            </h2>
            <p className="mt-4 text-slate-500">
              Every assigned category comes with the exact rules that fired —
              circularity, margin variance, orientation, diameter — plus
              per-feature importance, aligned to the ACR BI-RADS Atlas. No
              black box between the pixels and the score.
            </p>
            <ul className="mt-6 space-y-3">
              {[
                "Rules that fired, in plain language",
                "Per-feature importance ranking",
                "Aligned to the ACR BI-RADS Atlas",
              ].map((t) => (
                <li key={t} className="flex items-start gap-2.5 text-sm text-slate-600">
                  <FiCheckCircle className="mt-0.5 shrink-0 text-brand-600" />
                  {t}
                </li>
              ))}
            </ul>
          </Reveal>
          <Reveal delay={120}>
            <BrowserMock
              url="exbi-rads.app / study · BI-RADS"
              image={biradsShot}
              alt="Why BI-RADS 4 — rules that fired"
            />
          </Reveal>
        </div>
      </section>

      {/* ================= ER-status spotlight ================= */}
      <section className="py-16">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <Reveal className="order-2 lg:order-1">
            <BrowserMock
              url="exbi-rads.app / study · ER status"
              image={erShot}
              alt="ER status prediction"
            />
          </Reveal>
          <Reveal delay={120} className="order-1 lg:order-2">
            <Eyebrow>ER-status prediction</Eyebrow>
            <h2 className="mt-2 text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl">
              An early hormone-receptor signal — before IHC
            </h2>
            <p className="mt-4 text-slate-500">
              Seven routine clinical inputs from a basic hospital workup — no
              immunohistochemistry required — produce an ER+/ER− prediction
              with confidence banding, so treatment planning can start while
              pathology is pending.
            </p>
            <ul className="mt-6 space-y-3">
              {[
                "No IHC needed — routine workup only",
                "Confidence banding on every prediction",
                "Per-input contribution flags (ER+ / ER−)",
              ].map((t) => (
                <li key={t} className="flex items-start gap-2.5 text-sm text-slate-600">
                  <FiCheckCircle className="mt-0.5 shrink-0 text-brand-600" />
                  {t}
                </li>
              ))}
            </ul>
          </Reveal>
        </div>
      </section>

      {/* ================= Clinical safety ================= */}
      <FullBleed id="clinical-safety" className="my-8 bg-gradient-to-br from-brand-900 to-brand-800 py-20 text-white">
        <Reveal className="mx-auto max-w-3xl text-center">
          <span className="mx-auto grid h-12 w-12 place-items-center rounded-full border border-brand-300/50 text-brand-300">
            <FiShield size={22} />
          </span>
          <Eyebrow dark className="mt-4">
            Clinical safety
          </Eyebrow>
          <h2 className="mt-3 text-2xl font-extrabold tracking-tight sm:text-3xl">
            A decision-support aid — not an autonomous diagnostic device.
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-brand-100/90">
            Every output — segmentation mask, BI-RADS category, ER-status
            prediction and generated report — must be reviewed and signed off
            by a qualified clinician before any clinical decision. The system
            is designed to make that review faster and more transparent,
            never to replace it.
          </p>
          <div className="mt-7 flex flex-wrap items-center justify-center gap-3">
            {SAFETY_BADGES.map((b) => (
              <span
                key={b}
                className="rounded-full border border-white/25 px-4 py-1.5 font-mono text-xs text-brand-100"
              >
                {b}
              </span>
            ))}
          </div>
        </Reveal>
      </FullBleed>

      {/* ================= Team ================= */}
      <section id="team" className="py-24">
        <Reveal className="mx-auto max-w-2xl text-center">
          <Eyebrow>The team</Eyebrow>
          <h2 className="mt-2 text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl">
            Built by people who read the scans
          </h2>
          <p className="mt-3 text-slate-500">
            Drop in your photos and edit the names — this section is fully
            editable.
          </p>
        </Reveal>

        <div className="mt-14 grid gap-5 sm:grid-cols-3">
          {[
            {
              name: user?.name || "Pasindu Iroshan",
              role: "Lead developer",
              desc: "Pipeline architecture, segmentation and white-box classifier.",
              photo: user?.picture,
            },
            { name: "Team member", role: "Role", desc: "Edit this card with their focus area." },
            { name: "Team member", role: "Role", desc: "Edit this card with their focus area." },
          ].map((m, i) => (
            <Reveal key={i} delay={i * 90}>
              <div className="h-full rounded-2xl border border-slate-200 bg-white p-6 text-center shadow-sm transition-shadow hover:shadow-md">
                {m.photo ? (
                  <img
                    src={m.photo}
                    alt={m.name}
                    className="mx-auto h-20 w-20 rounded-full object-cover ring-2 ring-brand-100"
                  />
                ) : (
                  <span className="mx-auto grid h-20 w-20 place-items-center rounded-full border-2 border-dashed border-slate-200 text-slate-300">
                    <FiImage size={22} />
                  </span>
                )}
                <h3 className="mt-4 text-base font-bold text-slate-900">{m.name}</h3>
                <p className="text-[11px] font-bold uppercase tracking-wide text-brand-600">
                  {m.role}
                </p>
                <p className="mt-2 text-sm leading-relaxed text-slate-500">{m.desc}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ================= Contact ================= */}
      <FullBleed id="contact" className="mb-8 bg-white py-20">
        <Reveal className="mx-auto max-w-2xl text-center">
          <Eyebrow>Get in touch</Eyebrow>
          <h2 className="mt-2 text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl">
            Interested in ExBI-RADS for your department?
          </h2>
          <p className="mt-4 text-slate-500">
            Write to us for a walkthrough of the pipeline, validation
            details, or collaboration on clinical evaluation.
          </p>
          <a
            href="mailto:hello@exbi-rads.app"
            className="group mt-8 inline-flex items-center gap-2 rounded-xl bg-brand-600 px-6 py-3 text-sm font-bold text-white shadow-sm shadow-brand-600/30 transition-all duration-200 hover:-translate-y-0.5 hover:bg-brand-700 hover:shadow-lg"
          >
            <FiMail /> hello@exbi-rads.app
          </a>
        </Reveal>
      </FullBleed>
    </div>
  );
}
