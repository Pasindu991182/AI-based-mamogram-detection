import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

// The access token lives in memory only — never in localStorage, where any
// injected script could read it. The session itself is an httpOnly cookie the
// browser sends to /auth/* (hence withCredentials); a page reload restores the
// access token from it via refreshSession().
let accessToken = null;
let onSessionExpired = () => {};

export function setSessionExpiredHandler(fn) {
  onSessionExpired = fn;
}

export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  withCredentials: true,
});

// Stored image URLs come back as signed, relative paths (`/uploads/...?sig=`).
// They are served by the API, not the dev server, so point them at the API
// origin. Absolute URLs are left as-is.
export function mediaUrl(path) {
  if (!path) return path;
  return /^https?:\/\//.test(path) ? path : `${API_URL}${path}`;
}

// Attach the JWT to every request.
api.interceptors.request.use((config) => {
  if (accessToken) config.headers.Authorization = `Bearer ${accessToken}`;
  return config;
});

// Access tokens are short-lived: on a 401, renew once from the session cookie
// and replay the request. If the session itself is gone, send the user to login.
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    const isAuthCall = /^\/auth\/(login|refresh|logout)$/.test(original?.url ?? "");
    if (error.response?.status !== 401 || !original || original._retried || isAuthCall) {
      return Promise.reject(error);
    }
    original._retried = true;
    try {
      await refreshSession();
    } catch {
      onSessionExpired();
      return Promise.reject(error);
    }
    return api(original);
  }
);

// ---- Auth ----
function adoptSession(data) {
  accessToken = data.access_token;
  return data;
}

export async function login(email, password) {
  const { data } = await api.post("/auth/login", { email, password });
  return adoptSession(data);
}

// Single-flight: concurrent callers (parallel 401s, StrictMode's double effect)
// share one request.
let refreshInFlight = null;
export function refreshSession() {
  refreshInFlight ??= api
    .post("/auth/refresh")
    .then(({ data }) => adoptSession(data))
    .catch((err) => {
      accessToken = null;
      throw err;
    })
    .finally(() => {
      refreshInFlight = null;
    });
  return refreshInFlight;
}

export async function logout() {
  try {
    await api.post("/auth/logout");
  } finally {
    accessToken = null;
  }
}

export async function changePassword(currentPassword, newPassword) {
  const { data } = await api.post("/auth/change-password", {
    current_password: currentPassword,
    new_password: newPassword,
  });
  return adoptSession(data);
}

// ---- Admin: overview, audit trail, user provisioning ----
export async function getAdminOverview() {
  const { data } = await api.get("/admin/overview");
  return data;
}

export async function getAuditTrail(limit = 50) {
  const { data } = await api.get("/admin/audit", { params: { limit } });
  return data;
}

export async function listUsers() {
  const { data } = await api.get("/admin/users");
  return data;
}

export async function createUser(payload) {
  const { data } = await api.post("/admin/users", payload);
  return data;
}

export async function updateUser(userId, payload) {
  const { data } = await api.patch(`/admin/users/${userId}`, payload);
  return data;
}

export async function resetUserPassword(userId, password) {
  const { data } = await api.post(`/admin/users/${userId}/reset-password`, { password });
  return data;
}

// FastAPI errors carry a `detail` string (or a validation list).
export function errorMessage(error, fallback = "Something went wrong.") {
  const detail = error?.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg;
  return fallback;
}

// ---- Tier 1-3 ----
export async function analyze(patientAge, ccFile, mloFile, caseId) {
  const form = new FormData();
  form.append("patient_age", String(patientAge));
  if (caseId != null) form.append("case_id", String(caseId));
  if (ccFile) form.append("file_cc", ccFile);
  if (mloFile) form.append("file_mlo", mloFile);
  const { data } = await api.post("/analyze", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

// ---- CBR (Case-Based Reasoning) ----
export async function getSimilarCases(features, biradsCode, patientAge, topK = 3) {
  const { data } = await api.post("/cbr/similar-cases", {
    features,
    birads_code: biradsCode,
    patient_age: patientAge,
    top_k: topK,
  });
  return data;
}

export async function getCbrReferenceLibrary() {
  const { data } = await api.get("/cbr/reference-library");
  return data;
}

// ---- Tier 4 ----
export async function generateReport(payload) {
  const { data } = await api.post("/report/generate", payload);
  return data;
}

export async function updateReport(reportId, editedText, finalize = false) {
  const { data } = await api.put(`/report/${reportId}`, {
    edited_text: editedText,
    finalize,
  });
  return data;
}

// ---- Tier 5 ----
export async function predictER(payload) {
  const { data } = await api.post("/er/predict", payload);
  return data;
}

// ---- Cases ----
export async function listCases(patientRef) {
  const { data } = await api.get("/cases", {
    params: patientRef ? { patient_ref: patientRef } : undefined,
  });
  return data;
}

export async function createCase(payload) {
  const { data } = await api.post("/cases", payload);
  return data;
}

export async function getCase(caseId) {
  const { data } = await api.get(`/cases/${caseId}`);
  return data;
}

export async function updateCase(caseId, payload) {
  const { data } = await api.patch(`/cases/${caseId}`, payload);
  return data;
}

export async function deleteCase(caseId) {
  await api.delete(`/cases/${caseId}`);
}

export async function getCaseDetail(caseId) {
  const { data } = await api.get(`/cases/${caseId}/detail`);
  return data;
}

// ---- Tier 6: Clinical RAG assistant ----
export async function getChatStatus() {
  const { data } = await api.get("/chat/status");
  return data;
}

export async function askAssistant(message, sessionId, caseId) {
  const { data } = await api.post("/chat", {
    message,
    session_id: sessionId,
    case_id: caseId ?? null,
  });
  return data;
}
