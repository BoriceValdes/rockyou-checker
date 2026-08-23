export function PrivacyExplainer() {
  return (
    <div className="rounded-xl border border-white/10 bg-ink-light/60 p-5">
      <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-signal-soft">
        Comment votre mot de passe reste privé
      </p>

      <div className="flex flex-col gap-2 font-mono text-xs sm:flex-row sm:items-center sm:gap-3">
        <span className="rounded bg-white/5 px-2 py-1 text-slate-400">"••••••••••"</span>
        <span className="text-slate-600">→ Algorithme →</span>
        <span className="flex overflow-hidden rounded border border-white/10">
          <span className="bg-signal/30 px-2 py-1 text-signal-soft">fzefezfghfhfhf</span>
          <span className="bg-white/5 px-2 py-1 text-slate-500">aefaefeafeafaefefeafefefef</span>
        </span>
      </div>

      <p className="mt-3 text-sm leading-relaxed text-slate-400">
        Seul le une partie de votre mot de passe est envoyé au serveur.
        La comparaison finale se fait localement : votre mot de passe 
        et son hash complet ne transitent jamais sur le réseau.
      </p>
    </div>
  );
}
