import type { AnssiAnalysis, AnssiSeverity } from "../types/domain";

const SEVERITY_LABEL: Record<AnssiSeverity, string> = {
  ok: "Conforme aux recommandations ANSSI",
  weak: "Partiellement conforme",
  critical: "Non conforme — mot de passe faible",
};

const SEVERITY_COLOR: Record<AnssiSeverity, string> = {
  ok: "text-emerald-400",
  weak: "text-amber-400",
  critical: "text-alert",
};

export function AnssiChecklist({ anssi }: { anssi: AnssiAnalysis }) {
  return (
    <div className="rounded-xl border border-white/10 bg-ink-light p-5">
      <div className="mb-4 flex items-center justify-between">
        <p className={`font-semibold ${SEVERITY_COLOR[anssi.severity]}`}>
          {SEVERITY_LABEL[anssi.severity]}
        </p>
        <span className="font-mono text-sm text-slate-400">{anssi.score}/100</span>
      </div>

      <div className="mb-4 h-2 w-full overflow-hidden rounded-full bg-white/5">
        <div
          className={`h-full transition-all ${
            anssi.severity === "ok"
              ? "bg-emerald-400"
              : anssi.severity === "weak"
                ? "bg-amber-400"
                : "bg-alert"
          }`}
          style={{ width: `${anssi.score}%` }}
        />
      </div>

      <ul className="space-y-2">
        {anssi.rules.map((rule) => (
          <li key={rule.code} className="flex items-center gap-2 text-sm">
            <span className={rule.passed ? "text-emerald-400" : "text-slate-600"}>
              {rule.passed ? "✔️" : "○"}
            </span>
            <span className={rule.passed ? "text-slate-200" : "text-slate-500"}>
              {rule.label}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
