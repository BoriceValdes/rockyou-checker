export function PrivacyExplainer() {
  return (
    <div className="rounded-xl border border-white/10 bg-ink-light/60 p-5">
      <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-signal-soft">
        Comment votre mot de passe reste privé
      </p>

      <div className="flex flex-col gap-2 font-mono text-xs sm:flex-row sm:items-center sm:gap-3">
        <span className="rounded bg-white/5 px-2 py-1 text-slate-400">"••••••••••"</span>
        <span className="text-slate-600">→ SHA-1 →</span>
        <span className="flex overflow-hidden rounded border border-white/10">
          <span className="bg-signal/30 px-2 py-1 text-signal-soft">5BAA6</span>
          <span className="bg-white/5 px-2 py-1 text-slate-500">1E4C9B93F3F0682250B6CF8331B7EE68FD8</span>
        </span>
      </div>

      <p className="mt-3 text-sm leading-relaxed text-slate-400">
        Le hash SHA-1 est calculé <strong className="text-slate-200">dans votre navigateur</strong>.
        Seul le préfixe en surbrillance (5 caractères) est envoyé au serveur, qui répond avec
        toutes les fins de hash connues pour ce préfixe. La comparaison finale se fait
        localement : votre mot de passe et son hash complet ne transitent jamais sur le réseau.
      </p>
    </div>
  );
}
