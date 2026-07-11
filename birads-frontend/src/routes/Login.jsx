import { useState } from "react";
import { GoogleLogin } from "@react-oauth/google";
import { Navigate, useNavigate } from "react-router-dom";
import { FiLock, FiShield } from "react-icons/fi";
import { FcGoogle } from "react-icons/fc";
import { useAuth } from "@/hooks/useAuth";
import Brand from "@/components/Brand";
import doctorImg from "@/assets/doctorimage.png";

const PIPELINE = [
  ["Segment", "Attention U-Net isolates the lesion"],
  ["Measure", "6 radiomic morphology features"],
  ["Classify", "White-box BI-RADS + the reasons why"],
  ["Predict", "ER status for early treatment planning"],
];

export default function Login() {
  const { user, loginWithGoogleCredential } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState("");

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
            Use your hospital Google account to continue. Every study is signed
            to a named radiologist.
          </p>

          <div className="mt-8 flex items-center gap-3 text-[11px] font-semibold uppercase tracking-wide text-slate-400">
            <span className="h-px flex-1 bg-slate-200" />
            <span className="flex items-center gap-1.5">
              <FcGoogle size={16} /> Continue with Google
            </span>
            <span className="h-px flex-1 bg-slate-200" />
          </div>

          <div className="mt-5 flex justify-center">
            <GoogleLogin
              shape="pill"
              width="320"
              onSuccess={async (cred) => {
                try {
                  if (!cred.credential) throw new Error("No credential");
                  await loginWithGoogleCredential(cred.credential);
                  navigate("/");
                } catch {
                  setError("Login failed. Please try again.");
                }
              }}
              onError={() => setError("Google sign-in was cancelled or failed.")}
            />
          </div>

          {error && (
            <p className="mt-6 rounded-lg bg-red-50 p-3 text-sm font-medium text-red-700">
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
