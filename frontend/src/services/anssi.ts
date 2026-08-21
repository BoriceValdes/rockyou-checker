import type { AnssiAnalysis, AnssiRuleResult, AnssiSeverity } from "../types/domain";
import rulesSpec from "../anssi-rules.json";

/**
 * Analyse ANSSI d'un mot de passe.
 *
 * Les règles elles-mêmes (seuils, motifs, jeux de caractères) sont définies
 * une seule fois en données dans anssi-rules.json et interprétées ici. La
 * même analyse tourne aussi côté backend (app/anssi.py, backend/app/
 * anssi_rules.json) à des fins de tests unitaires et de réutilisation
 * potentielle, mais volontairement jamais via une route HTTP recevant un
 * mot de passe en clair : c'est ici, dans le navigateur, que ça doit
 * tourner. Un test (backend/tests/test_anssi_rules_sync.py) garantit que
 * les deux copies du fichier de règles restent identiques.
 */

interface Rule {
  code: string;
  label: string;
  type: string;
  value?: number;
  chars?: string;
  patterns?: string[];
  window?: number;
  max_run?: number;
}

type Check = (pwd: string, rule: Rule) => boolean;

const CHECKS: Record<string, Check> = {
  min_length: (pwd, rule) => pwd.length >= rule.value!,
  has_lower: (pwd) => /[a-z]/.test(pwd),
  has_upper: (pwd) => /[A-Z]/.test(pwd),
  has_digit: (pwd) => /[0-9]/.test(pwd),
  has_any_char: (pwd, rule) => [...pwd].some((c) => (rule.chars!).includes(c)),
  no_sequence: (pwd, rule) => {
    const lowered = pwd.toLowerCase();
    const window = rule.window!;
    return !rule.patterns!.some((pattern) => {
      for (let i = 0; i <= pattern.length - window; i++) {
        if (lowered.includes(pattern.slice(i, i + window))) return true;
      }
      return false;
    });
  },
  no_repeated_char: (pwd, rule) => {
    const maxRun = rule.max_run!;
    let run = 1;
    for (let i = 1; i < pwd.length; i++) {
      run = pwd[i] === pwd[i - 1] ? run + 1 : 1;
      if (run > maxRun) return false;
    }
    return true;
  },
};

export function analyzeAnssi(password: string): AnssiAnalysis {
  const rules: AnssiRuleResult[] = rulesSpec.rules.map((r: Rule) => ({
    code: r.code,
    label: r.label,
    passed: CHECKS[r.type](password, r),
  }));

  const passedCount = rules.filter((r) => r.passed).length;
  const score = Math.round((100 * passedCount) / rules.length);

  const { ok_score: okScore, weak_min_score: weakMinScore } = rulesSpec.severity_thresholds;
  let severity: AnssiSeverity;
  if (score >= okScore) severity = "ok";
  else if (score >= weakMinScore) severity = "weak";
  else severity = "critical";

  return { score, severity, rules, isCompliant: rules.every((r) => r.passed) };
}
