import { useEffect, useRef, useState } from "react";
import { FiMessageSquare, FiX, FiSend, FiAlertCircle } from "react-icons/fi";
import { askAssistant, getChatStatus } from "@/lib/api";

// One conversation memory id per browser tab session.
const SESSION_ID = `web-${Math.random().toString(36).slice(2, 10)}`;

const WELCOME = {
  role: "assistant",
  text:
    "Hi — I'm your clinical assistant. Ask me about BI-RADS categories, " +
    "treatment guidelines, or ER/HER2 testing. I answer only from the loaded " +
    "guideline documents.",
  sources: [],
};

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([WELCOME]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null); // {ready, key_configured, index_ready}
  const scrollRef = useRef(null);

  // Load assistant readiness the first time the panel opens.
  useEffect(() => {
    if (open && status === null) {
      getChatStatus()
        .then(setStatus)
        .catch(() => setStatus({ ready: false, key_configured: false, index_ready: false }));
    }
  }, [open, status]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  async function send() {
    const text = input.trim();
    if (!text || loading) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", text }]);
    setLoading(true);
    try {
      const res = await askAssistant(text, SESSION_ID);
      setMessages((m) => [
        ...m,
        { role: "assistant", text: res.answer, sources: res.sources ?? [] },
      ]);
    } catch (err) {
      const detail =
        err?.response?.data?.detail ??
        "Something went wrong reaching the assistant.";
      setMessages((m) => [
        ...m,
        { role: "assistant", text: detail, sources: [], error: true },
      ]);
    } finally {
      setLoading(false);
    }
  }

  const notReady = status && !status.ready;

  return (
    <>
      {/* Floating toggle button */}
      <button
        onClick={() => setOpen((o) => !o)}
        title="Clinical assistant"
        className="no-print fixed bottom-5 right-5 z-30 grid h-14 w-14 place-items-center rounded-full bg-brand-600 text-white shadow-lg shadow-brand-600/30 transition hover:bg-brand-700"
      >
        {open ? <FiX size={22} /> : <FiMessageSquare size={22} />}
      </button>

      {/* Chat panel */}
      {open && (
        <div className="no-print fixed bottom-24 right-5 z-30 flex h-[32rem] w-[92vw] max-w-sm flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl">
          <div className="flex items-center justify-between border-b border-slate-100 bg-brand-600 px-4 py-3 text-white">
            <div className="flex items-center gap-2">
              <FiMessageSquare />
              <span className="font-bold">Clinical Assistant</span>
            </div>
            <span className="rounded-full bg-white/20 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide">
              RAG · guidelines
            </span>
          </div>

          {notReady && (
            <div className="flex items-start gap-2 border-b border-amber-200 bg-amber-50 px-4 py-2 text-xs text-amber-800">
              <FiAlertCircle className="mt-0.5 shrink-0" />
              <span>
                Assistant not configured yet.{" "}
                {!status.key_configured && "Set OPENAI_API_KEY. "}
                {!status.index_ready &&
                  "Build the index: python -m scripts.build_rag_index."}
              </span>
            </div>
          )}

          <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-3.5 py-2 text-sm leading-relaxed ${
                    m.role === "user"
                      ? "bg-brand-600 text-white"
                      : m.error
                        ? "bg-red-50 text-red-700"
                        : "bg-slate-100 text-slate-800"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{m.text}</p>
                  {m.sources?.length > 0 && (
                    <p className="mt-2 border-t border-slate-200 pt-1.5 text-[10px] text-slate-500">
                      Sources: {m.sources.join(", ")}
                    </p>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="rounded-2xl bg-slate-100 px-3.5 py-2 text-sm text-slate-400">
                  Thinking…
                </div>
              </div>
            )}
          </div>

          <div className="border-t border-slate-100 p-3">
            <div className="flex items-end gap-2">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    send();
                  }
                }}
                rows={1}
                placeholder="Ask about BI-RADS, treatment, ER status…"
                className="max-h-24 flex-1 resize-none rounded-xl border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
              <button
                onClick={send}
                disabled={loading || !input.trim()}
                className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-brand-600 text-white transition hover:bg-brand-700 disabled:opacity-40"
              >
                <FiSend size={16} />
              </button>
            </div>
            <p className="mt-1.5 text-center text-[10px] text-slate-400">
              Aid only — not a diagnosis. Keep a clinician in the loop.
            </p>
          </div>
        </div>
      )}
    </>
  );
}
