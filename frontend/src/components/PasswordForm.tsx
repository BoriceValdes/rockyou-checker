import { FormEvent, useState } from "react";

interface Props {
  onSubmit: (password: string) => void;
  loading: boolean;
}

export function PasswordForm({ onSubmit, loading }: Props) {
  const [password, setPassword] = useState("");
  const [visible, setVisible] = useState(false);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    onSubmit(password);
  }

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <label htmlFor="password" className="mb-2 block text-sm font-medium text-slate-300">
        Mot de passe à analyser
      </label>
      <div className="flex items-stretch gap-2">
        <div className="relative flex-1">
          <input
            id="password"
            name="password"
            type={visible ? "text" : "password"}
            autoComplete="off"
            spellCheck={false}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="..........."
            className="w-full rounded-lg border border-white/10 bg-ink-light px-4 py-3 font-mono text-lg text-slate-100 outline-none ring-signal/50 placeholder:text-slate-600 focus:ring-2"
          />
          <button
            type="button"
            onClick={() => setVisible((v) => !v)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-medium text-slate-400 hover:text-slate-200"
            aria-label={visible ? "Masquer le mot de passe" : "Afficher le mot de passe"}
          >
            {visible ? "Masquer" : "Afficher"}
          </button>
        </div>
        <button
          type="submit"
          disabled={loading}
          className="shrink-0 rounded-lg bg-signal px-6 py-3 font-semibold text-white transition hover:bg-signal-soft disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? "Analyse..." : "Analyser"}
        </button>
      </div>
    </form>
  );
}
