export type AnssiSeverity = "ok" | "weak" | "critical";

export interface AnssiRuleResult {
  code: string;
  label: string;
  passed: boolean;
}

export interface AnssiAnalysis {
  score: number;
  severity: AnssiSeverity;
  rules: AnssiRuleResult[];
  isCompliant: boolean;
}

export interface BreachResult {
  isCompromised: boolean;
  occurrenceCount: number;
}

export interface PasswordAnalysis {
  breach: BreachResult;
  anssi: AnssiAnalysis;
}
