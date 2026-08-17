import type { BreachResult } from "../types/domain";

export function BreachResultCard({ breach }: { breach: BreachResult }) {
  if (breach.isCompromised) {
    return (
      <div className="rounded-xl border border-alert/40 bg-alert/10 p-5">
        <div className="flex items-center gap-3">
          <span className="text-2xl">⚠️</span>
          <div>
            <p className="font-semibold text-alert">Mot de passe compromis</p>
            <p className="mt-1 text-sm text-slate-300">
              Ce mot de passe apparaît{" "}
              <span className="font-mono text-slate-100">
                {breach.occurrenceCount.toLocaleString("fr-FR")}
              </span>{" "}
              fois dans le corpus RockYou. Il est fortement recommandé de ne plus l'utiliser.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-emerald-400/30 bg-emerald-400/10 p-5">
      <div className="flex items-center gap-3">
        <span className="text-2xl">✅</span>
        <div>
          <p className="font-semibold text-emerald-400">Absent de la base RockYou</p>
          <p className="mt-1 text-sm text-slate-300">
            Ce mot de passe n'a pas été trouvé dans le corpus RockYou analysé.
          </p>
        </div>
      </div>
    </div>
  );
}
