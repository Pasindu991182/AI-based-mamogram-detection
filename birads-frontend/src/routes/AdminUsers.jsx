import { useCallback, useEffect, useState } from "react";
import { Link, Navigate } from "react-router-dom";
import { FiArrowLeft, FiKey, FiPlus, FiSlash, FiUserCheck } from "react-icons/fi";
import {
  createUser,
  errorMessage,
  listUsers,
  resetUserPassword,
  updateUser,
} from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import Button from "@/components/Button";
import Modal from "@/components/Modal";

const labelCls =
  "mb-1 block text-[11px] font-bold uppercase tracking-wide text-slate-500";
const inputCls =
  "w-full rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium focus:border-brand-500 focus:outline-none";
const GRID =
  "grid grid-cols-[1.3fr_1.5fr_0.8fr_0.5fr_1fr_1fr_auto] items-center gap-2 px-5";
const iconBtn =
  "grid h-8 w-8 place-items-center rounded-lg text-slate-400 transition disabled:opacity-30 disabled:pointer-events-none";

const EMPTY_FORM = { name: "", email: "", role: "radiologist", password: "" };

function statusOf(u) {
  if (!u.is_active) return ["Deactivated", "text-slate-400"];
  if (u.locked) return ["Locked", "text-red-600"];
  if (u.must_change_password) return ["Temporary password", "text-orange-600"];
  return ["Active", "text-brand-700"];
}

export default function AdminUsers() {
  const { user: me } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [resetting, setResetting] = useState(null); // user being reset
  const [tempPassword, setTempPassword] = useState("");
  const [modalError, setModalError] = useState("");
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    try {
      setUsers(await listUsers());
      setError("");
    } catch (err) {
      setError(errorMessage(err, "Could not load users."));
    } finally {
      setLoading(false);
    }
  }, []);

  const isAdmin = me?.role === "admin";
  useEffect(() => {
    if (isAdmin) load();
  }, [isAdmin, load]);

  if (!isAdmin) return <Navigate to="/" replace />;

  async function run(action, onDone) {
    setModalError("");
    setSaving(true);
    try {
      await action();
      onDone?.();
      await load();
    } catch (err) {
      const message = errorMessage(err);
      // Row actions have no modal open to show the message in.
      if (onDone) setModalError(message);
      else setError(message);
    } finally {
      setSaving(false);
    }
  }

  function closeModals() {
    setCreating(false);
    setResetting(null);
    setForm(EMPTY_FORM);
    setTempPassword("");
    setModalError("");
  }

  return (
    <div>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <Link
            to="/admin"
            className="mb-2 inline-flex items-center gap-1 text-xs font-semibold text-slate-500 hover:text-brand-700"
          >
            <FiArrowLeft /> Admin dashboard
          </Link>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">
            Users
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Accounts are issued here — there is no public sign-up. New users
            must replace their temporary password at first sign-in.
          </p>
        </div>
        <Button icon={FiPlus} onClick={() => setCreating(true)}>
          Add user
        </Button>
      </div>

      {error && (
        <div
          role="alert"
          className="mt-4 rounded-lg border-l-4 border-red-500 bg-red-50 p-3 text-sm font-medium text-red-700"
        >
          {error}
        </div>
      )}

      <div className="mt-5 overflow-x-auto rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="min-w-[820px]">
          <div
            className={`${GRID} border-b border-slate-100 bg-slate-50 py-3 text-[11px] font-bold uppercase tracking-wide text-slate-400`}
          >
            <span>Name</span>
            <span>Email</span>
            <span>Role</span>
            <span>Cases</span>
            <span>Last sign-in</span>
            <span>Status</span>
            <span className="text-right">Actions</span>
          </div>

          {loading ? (
            <div className="px-5 py-16 text-center text-sm text-slate-400">
              Loading…
            </div>
          ) : (
            users.map((u) => {
              const [label, tone] = statusOf(u);
              const isSelf = u.id === me.id;
              return (
                <div
                  key={u.id}
                  className={`${GRID} border-b border-slate-50 py-3.5 text-sm last:border-0`}
                >
                  <span className="font-semibold text-slate-800">
                    {u.name}
                    {isSelf && (
                      <span className="font-normal text-slate-400"> (you)</span>
                    )}
                  </span>
                  <span className="truncate font-mono text-xs text-slate-500">
                    {u.email}
                  </span>
                  <span className="capitalize text-slate-600">{u.role}</span>
                  <span className="font-mono text-xs text-slate-600">
                    {u.case_count}
                  </span>
                  <span className="text-xs text-slate-500">
                    {u.last_login_at
                      ? new Date(u.last_login_at).toLocaleString()
                      : "Never"}
                  </span>
                  <span className={`text-xs font-semibold ${tone}`}>{label}</span>
                  <span className="flex items-center justify-end gap-1">
                    <button
                      title="Issue a temporary password"
                      aria-label={`Reset password for ${u.name}`}
                      onClick={() => setResetting(u)}
                      className={`${iconBtn} hover:bg-brand-50 hover:text-brand-700`}
                    >
                      <FiKey />
                    </button>
                    <button
                      title={u.is_active ? "Deactivate" : "Reactivate"}
                      aria-label={`${u.is_active ? "Deactivate" : "Reactivate"} ${u.name}`}
                      disabled={isSelf || saving}
                      onClick={() =>
                        run(() => updateUser(u.id, { is_active: !u.is_active }))
                      }
                      className={`${iconBtn} ${
                        u.is_active
                          ? "hover:bg-red-50 hover:text-red-600"
                          : "hover:bg-brand-50 hover:text-brand-700"
                      }`}
                    >
                      {u.is_active ? <FiSlash /> : <FiUserCheck />}
                    </button>
                  </span>
                </div>
              );
            })
          )}
        </div>
      </div>

      <Modal open={creating} onClose={closeModals} title="Add user">
        <form
          className="space-y-4"
          onSubmit={(e) => {
            e.preventDefault();
            run(() => createUser(form), closeModals);
          }}
        >
          <label className="block">
            <span className={labelCls}>Full name</span>
            <input
              required
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className={inputCls}
            />
          </label>
          <label className="block">
            <span className={labelCls}>Email</span>
            <input
              type="email"
              required
              autoComplete="off"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              className={inputCls}
            />
          </label>
          <label className="block">
            <span className={labelCls}>Role</span>
            <select
              value={form.role}
              onChange={(e) => setForm({ ...form, role: e.target.value })}
              className={inputCls}
            >
              <option value="radiologist">Radiologist</option>
              <option value="admin">Administrator</option>
            </select>
          </label>
          <TempPasswordField
            value={form.password}
            onChange={(password) => setForm({ ...form, password })}
          />
          <ModalFooter error={modalError} saving={saving} onCancel={closeModals}>
            Create user
          </ModalFooter>
        </form>
      </Modal>

      <Modal
        open={Boolean(resetting)}
        onClose={closeModals}
        title={`Reset password — ${resetting?.name ?? ""}`}
      >
        <form
          className="space-y-4"
          onSubmit={(e) => {
            e.preventDefault();
            run(() => resetUserPassword(resetting.id, tempPassword), closeModals);
          }}
        >
          <p className="text-sm text-slate-600">
            This signs the user out everywhere and clears any lockout.
          </p>
          <TempPasswordField value={tempPassword} onChange={setTempPassword} />
          <ModalFooter error={modalError} saving={saving} onCancel={closeModals}>
            Reset password
          </ModalFooter>
        </form>
      </Modal>
    </div>
  );
}

function TempPasswordField({ value, onChange }) {
  return (
    <label className="block">
      <span className={labelCls}>Temporary password</span>
      <input
        type="text"
        required
        minLength={12}
        autoComplete="off"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={`${inputCls} font-mono`}
      />
      <span className="mt-1 block text-xs text-slate-400">
        At least 12 characters, with letters and numbers. Pass it to the user
        in person; they must change it at next sign-in.
      </span>
    </label>
  );
}

function ModalFooter({ error, saving, onCancel, children }) {
  return (
    <>
      {error && (
        <p
          role="alert"
          className="rounded-lg bg-red-50 p-3 text-sm font-medium text-red-700"
        >
          {error}
        </p>
      )}
      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" disabled={saving}>
          {saving ? "Saving…" : children}
        </Button>
      </div>
    </>
  );
}
