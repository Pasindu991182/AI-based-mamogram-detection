import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const TOKEN_KEY = "birads_token";

export const api = axios.create({ baseURL: `${API_URL}/api/v1` });

// Attach the JWT to every request.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// On 401, clear the stale token so the app redirects to login.
api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY);
    }
    return Promise.reject(error);
  }
);

export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (t) => localStorage.setItem(TOKEN_KEY, t),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

// ---- Auth ----
export async function loginWithGoogle(idToken) {
  const { data } = await api.post("/auth/google", { id_token: idToken });
  return data;
}

export async function fetchMe() {
  const { data } = await api.get("/auth/me");
  return data;
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
