import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FiKey } from "react-icons/fi";
import { useAuth } from "@/hooks/useAuth";
import { errorMessage } from "@/lib/api";
import Brand from "@/components/Brand";
import Button from "@/components/Button";

const labelCls =
  "mb-1 block text-[11px] font-bold uppercase tracking-wide text-slate-500";
const inputCls =
  "w-full rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium focus:border-brand-500 focus:outline-none";

export default function ChangePassword() {
  const { user, changePassword, logout } = useAuth();
  const navigate = useNavigate();
  const forced = Boolean(user?.must_change_password);

  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [confirm, setConfirm] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function onSubmit(e) {
    e.preventDefault();
    if (next !== confirm) {
      setError("The new passwords do not match.");
      return;
    }
    setError("");
    setSubmitting(true);
    try {
      await changePassword(current, next);
      navigate("/", { replace: true });
    } catch (err) {
      setError(errorMessage(err, "Could not change the password."));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#f1f5f4] p-6">
      <div className="w-full max-w-sm rounded-3xl border border-slate-200 bg-white p-8 shadow-xl">
        <Brand size={30} />
        <h1 className="mt-6 text-2xl font-extrabold tracking-tight text-slate-900">
          {forced ? "Set your password" : "Change password"}
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          {forced
            ? "Your administrator issued a temporary password. Choose your own before continuing."
            : "You will stay signed in here; other devices are signed out."}
        </p>

        <form onSubmit={onSubmit} className="mt-6 space-y-4">
          <label className="block">
            <span className={labelCls}>
              {forced ? "Temporary password" : "Current password"}
            </span>
            <input
              type="password"
              autoComplete="current-password"
              required
              autoFocus
              value={current}
              onChange={(e) => setCurrent(e.target.value)}
              className={inputCls}
            />
          </label>
          <label className="block">
            <span className={labelCls}>New password</span>
            <input
              type="password"
              autoComplete="new-password"
              required
              minLength={12}
              value={next}
              onChange={(e) => setNext(e.target.value)}
              className={inputCls}
            />
            <span className="mt-1 block text-xs text-slate-400">
              At least 12 characters, with letters and numbers.
            </span>
          </label>
          <label className="block">
            <span className={labelCls}>Confirm new password</span>
            <input
              type="password"
              autoComplete="new-password"
              required
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              className={inputCls}
            />
          </label>

          {error && (
            <p
              role="alert"
              className="rounded-lg bg-red-50 p-3 text-sm font-medium text-red-700"
            >
              {error}
            </p>
          )}

          <div className="flex items-center justify-between gap-2 pt-2">
            <Button
              type="button"
              variant="ghost"
              onClick={async () => {
                if (forced) {
                  await logout();
                  navigate("/login");
                } else {
                  navigate(-1);
                }
              }}
            >
              {forced ? "Sign out" : "Cancel"}
            </Button>
            <Button type="submit" icon={FiKey} disabled={submitting}>
              {submitting ? "Saving…" : "Save password"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
