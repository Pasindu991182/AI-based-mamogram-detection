import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { FiLock, FiLogIn, FiShield } from "react-icons/fi";
import { useAuth } from "@/hooks/useAuth";
import { errorMessage } from "@/lib/api";
import Button from "@/components/Button";
import Brand from "@/components/Brand";
import doctorImg from "@/assets/doctorimage.png";

const PIPELINE = [
  ["Segment", "Attention U-Net isolates the lesion"],
  ["Measure", "6 radiomic morphology features"],
  ["Classify", "White-box BI-RADS + the reasons why"],
  ["Predict", "ER status for early treatment planning"],
];

const labelCls =
  "mb-1 block text-[11px] font-bold uppercase tracking-wide text-slate-500";
const inputCls =
  "w-full rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium focus:border-brand-500 focus:outline-none";

export default function Login() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      setError(errorMessage(err, "Could not reach the server. Please try again."));
      setPassword("");
    } finally {
      setSubmitting(false);
    }
  }

  if (user) return <Navigate to="/" replace />;

  return (
    <div className="grid min-h-screen md:grid-cols-2">
      {/* Left — brand / value panel */}
      <div className="relative hidden flex-col justify-between overflow-hidden bg-linear-to-br from-brand-800 via-brand-700 to-brand-900 p-12 text-white md:flex">
        <div className="absolute -right-24 -top-24 h-80 w-80 rounded-full bg-white/10 blur-2xl" />

        <div className="relative z-10">
          <Brand size={34} light />
        </div>

        <div className="relative z-10 max-w-md drop-shadow-md">
          <h1 className="text-3xl font-extrabold leading-tight">
            Explainable breast-cancer diagnostics, end to end.
          </h1>
          <p className="mt-3 text-brand-100">
            A transparent 4-tier pipeline: scan → segment → measure → classify →
            predict → report. Every decision shows its working.
          </p>

          <ul className="mt-8 space-y-3">
            {PIPELINE.map(([title, desc]) => (
              <li key={title} className="flex items-start gap-3">
                <span className="mt-1 grid h-5 w-5 shrink-0 place-items-center rounded-full bg-white/20 text-[11px] font-bold">
                  ✓
                </span>
                <div>
                  <span className="font-semibold">{title}</span>
                  <span className="text-brand-100"> — {desc}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>

        <div className="relative z-10 flex items-center gap-2 text-sm text-brand-100">
          <FiShield /> Encrypted · audit-logged · on-prem deployable
        </div>
      </div>

      {/* Right — sign-in card over the doctor image */}
      <div className="relative flex items-center justify-center overflow-hidden bg-[#f1f5f4] p-6">
        {/* Background image */}
        <img
          src={doctorImg}
          alt=""
          aria-hidden
          className="absolute inset-0 h-full w-full object-cover object-center"
        />
        {/* Soft light overlay so the white card stays crisp on top */}
        <div className="absolute inset-0 bg-white/40 backdrop-blur-[2px]" />

        <div className="relative z-10 w-full max-w-sm rounded-3xl border border-white/60 bg-white/95 p-8 shadow-2xl backdrop-blur">
          <div className="md:hidden">
            <Brand size={30} />
          </div>
          <h2 className="mt-6 text-2xl font-extrabold tracking-tight text-slate-900">
            Sign in
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            Use the account issued by your administrator. Every study is signed
            to a named radiologist.
          </p>

          <form onSubmit={onSubmit} className="mt-6 space-y-4">
            <label className="block">
              <span className={labelCls}>Email</span>
              <input
                type="email"
                autoComplete="username"
                required
                autoFocus
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className={inputCls}
              />
            </label>
            <label className="block">
              <span className={labelCls}>Password</span>
              <input
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={inputCls}
              />
            </label>
            <Button
              type="submit"
              icon={FiLogIn}
              disabled={submitting}
              className="w-full"
            >
              {submitting ? "Signing in…" : "Sign in"}
            </Button>
          </form>

          {error && (
            <p
              role="alert"
              className="mt-6 rounded-lg bg-red-50 p-3 text-sm font-medium text-red-700"
            >
              {error}
            </p>
          )}

          <div className="mt-8 flex items-center justify-center gap-2 text-xs text-slate-400">
            <FiLock /> Credentials never leave your institution
          </div>
          <div className="mt-6 border-t border-slate-100 pt-5 text-center text-[11px] leading-relaxed text-slate-400">
            © {new Date().getFullYear()} ExBI-RADS Engine · Final-year research
            project
            <br />
            <span className="text-slate-300">
              Decision-support aid — not for primary clinical diagnosis
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
