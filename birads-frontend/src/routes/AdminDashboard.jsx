import { useCallback, useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { FiRefreshCw, FiUsers } from "react-icons/fi";
import { errorMessage, getAdminOverview, getAuditTrail } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import Button from "@/components/Button";

// action → [label, tone]
const EVENTS = {
  login_success: ["Signed in", "text-brand-700"],
  login_failed: ["Failed sign-in", "text-red-600"],
  account_locked: ["Account locked", "text-red-600"],
  logout: ["Signed out", "text-slate-500"],
  password_changed: ["Changed password", "text-slate-700"],
  password_reset: ["Password reset by admin", "text-orange-600"],
  user_created: ["User created", "text-slate-700"],
  user_updated: ["User updated", "text-slate-700"],
  user_deactivated: ["User deactivated", "text-orange-600"],
  user_reactivated: ["User reactivated", "text-slate-700"],
};

const CASE_STATUSES = [
  ["draft", "Draft"],
  ["analyzed", "Analyzed"],
  ["reported", "Awaiting sign-off"],
  ["completed", "Signed"],
];

const GRID = "grid grid-cols-[1.1fr_1.2fr_1.6fr_1.4fr_0.8fr] items-center gap-2 px-5";

function Stat({ label, value, hint, alert }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="text-[11px] font-bold uppercase tracking-wide text-slate-400">
        {label}
      </div>
      <div
        className={`mt-2 text-3xl font-extrabold tracking-tight ${
          alert ? "text-red-600" : "text-slate-900"
        }`}
      >
        {value}
      </div>
      <div className="mt-1 text-xs text-slate-500">{hint}</div>
    </div>
  );
}

export default function AdminDashboard() {
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";
  const [overview, setOverview] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [o, e] = await Promise.all([getAdminOverview(), getAuditTrail(50)]);
      setOverview(o);
      setEvents(e);
      setError("");
    } catch (err) {
      setError(errorMessage(err, "Could not load the admin dashboard."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isAdmin) load();
  }, [isAdmin, load]);

  if (!isAdmin) return <Navigate to="/" replace />;

  const o = overview;
  return (
    <div>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">
            Admin dashboard
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Accounts, sessions and security events. Counts only — patient
            records stay with the radiologist who owns the case.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={load}
            title="Refresh"
            aria-label="Refresh"
            className="grid h-10 w-10 place-items-center rounded-xl border border-slate-200 bg-white text-slate-500 transition hover:bg-slate-50"
          >
            <FiRefreshCw className={loading ? "animate-spin" : ""} />
          </button>
          <Button as="link" to="/admin/users" icon={FiUsers}>
            Manage users
          </Button>
        </div>
      </div>

      {error && (
        <div
          role="alert"
          className="mt-4 rounded-lg border-l-4 border-red-500 bg-red-50 p-3 text-sm font-medium text-red-700"
        >
          {error}
        </div>
      )}

      {o && (
        <>
          <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Stat
              label="Active users"
              value={o.users_active}
              hint={`${o.users_total} accounts · ${o.users_admin} admin`}
            />
            <Stat
              label="Signed in now"
              value={o.sessions_active}
              hint="Open browser sessions"
            />
            <Stat
              label="Failed sign-ins (24h)"
              value={o.failed_logins_24h}
              hint={`${o.users_locked} account${o.users_locked === 1 ? "" : "s"} locked`}
              alert={o.users_locked > 0}
            />
            <Stat
              label="Temporary passwords"
              value={o.users_pending_password}
              hint="Issued but not yet changed"
            />
          </div>

          <div className="mt-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-baseline justify-between">
              <div className="text-[11px] font-bold uppercase tracking-wide text-slate-400">
                Cases
              </div>
              <div className="text-sm text-slate-500">
                <span className="font-bold text-slate-900">{o.cases_total}</span>{" "}
                total
              </div>
            </div>
            <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
              {CASE_STATUSES.map(([key, label]) => (
                <div key={key} className="rounded-xl bg-slate-50 px-4 py-3">
                  <div className="text-xl font-extrabold text-slate-900">
                    {o.cases_by_status[key] ?? 0}
                  </div>
                  <div className="text-xs text-slate-500">{label}</div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      <h2 className="mt-8 text-sm font-bold uppercase tracking-wide text-slate-500">
        Recent security events
      </h2>
      <div className="mt-3 overflow-x-auto rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="min-w-[760px]">
          <div
            className={`${GRID} border-b border-slate-100 bg-slate-50 py-3 text-[11px] font-bold uppercase tracking-wide text-slate-400`}
          >
            <span>When</span>
            <span>Event</span>
            <span>Account</span>
            <span>Affected</span>
            <span>IP address</span>
          </div>
          {events.length === 0 ? (
            <div className="px-5 py-12 text-center text-sm text-slate-400">
              {loading ? "Loading…" : "No events recorded yet."}
            </div>
          ) : (
            events.map((e) => {
              const [label, tone] = EVENTS[e.action] ?? [e.action, "text-slate-700"];
              return (
                <div
                  key={e.id}
                  className={`${GRID} border-b border-slate-50 py-3 text-sm last:border-0`}
                >
                  <span className="text-xs text-slate-500">
                    {new Date(e.created_at).toLocaleString()}
                  </span>
                  <span className={`font-semibold ${tone}`}>{label}</span>
                  <span className="truncate font-mono text-xs text-slate-600">
                    {e.actor_email || "—"}
                  </span>
                  <span className="truncate font-mono text-xs text-slate-500">
                    {e.target || "—"}
                  </span>
                  <span className="font-mono text-xs text-slate-500">
                    {e.ip_address || "—"}
                  </span>
                </div>
              );
            })
          )}
        </div>
      </div>
      <p className="mt-3 text-xs text-slate-400">Showing the latest 50 events.</p>
    </div>
  );
}
