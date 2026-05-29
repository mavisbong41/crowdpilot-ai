import { useState } from "react";
import { IconSend, IconSparkles } from "../icons.jsx";

export default function AIOperationsConsole({ initialMessages }) {
  const [messages, setMessages] = useState(initialMessages);
  const [input, setInput] = useState("");
  const [notice, setNotice] = useState(null);

  function handleSubmit(event) {
    event.preventDefault();
    const text = input.trim();
    if (!text) return;

    const userMessage = {
      id: `msg-${Date.now()}`,
      role: "user",
      content: text,
      time: new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setNotice("AI agents are not connected yet. Your message was saved locally for demo purposes.");

    setTimeout(() => setNotice(null), 5000);
  }

  return (
    <section
      aria-labelledby="console-heading"
      className="flex h-full min-h-[420px] flex-col rounded-2xl border border-slate-800 bg-surface-900 shadow-lg lg:min-h-0"
    >
      <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">
        <div className="flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-accent-500/30 to-indigo-500/20 text-accent-400">
            <IconSparkles className="h-4 w-4" />
          </span>
          <div>
            <h2 id="console-heading" className="text-sm font-semibold tracking-wide text-white">
              AI Operations Console
            </h2>
            <p className="text-xs text-slate-500">Multi-agent command interface</p>
          </div>
        </div>
        <span className="rounded-full border border-slate-700 bg-surface-800 px-2.5 py-0.5 text-[10px] font-medium uppercase tracking-wider text-slate-400">
          Preview
        </span>
      </div>

      <div className="flex flex-1 flex-col overflow-hidden">
        <div className="flex-1 space-y-3 overflow-y-auto p-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[90%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                  msg.role === "user"
                    ? "bg-accent-600 text-white"
                    : msg.role === "system"
                      ? "border border-slate-700 bg-surface-800 text-slate-400"
                      : "border border-slate-800 bg-surface-950 text-slate-300"
                }`}
              >
                {msg.role !== "user" && (
                  <p className="mb-1 text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                    {msg.role === "system" ? "System" : "CrowdPilot"}
                  </p>
                )}
                <p>{msg.content}</p>
                <p
                  className={`mt-1 text-[10px] ${
                    msg.role === "user" ? "text-sky-100/70" : "text-slate-600"
                  }`}
                >
                  {msg.time}
                </p>
              </div>
            </div>
          ))}
        </div>

        {notice && (
          <div className="mx-4 mb-2 rounded-lg border border-amber-500/30 bg-amber-500/10 px-3 py-2 text-xs text-amber-200">
            {notice}
          </div>
        )}

        <form onSubmit={handleSubmit} className="border-t border-slate-800/80 p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about crowd risk, staffing, or contingencies..."
              className="flex-1 rounded-xl border border-slate-700 bg-surface-950 px-4 py-2.5 text-sm text-white placeholder:text-slate-600 focus:border-accent-500 focus:outline-none focus:ring-1 focus:ring-accent-500/50"
            />
            <button
              type="submit"
              disabled={!input.trim()}
              className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-accent-600 text-white transition hover:bg-accent-500 disabled:cursor-not-allowed disabled:opacity-40"
              aria-label="Send message"
            >
              <IconSend className="h-4 w-4" />
            </button>
          </div>
          <p className="mt-2 text-center text-[10px] text-slate-600">
            GCP agent integration coming soon — mock mode active
          </p>
        </form>
      </div>
    </section>
  );
}
