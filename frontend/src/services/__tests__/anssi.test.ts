import { describe, expect, it } from "vitest";
import { analyzeAnssi } from "../anssi";

describe("analyzeAnssi", () => {
  it("marque un mot de passe faible comme critique", () => {
    const result = analyzeAnssi("azerty");
    expect(result.severity).toBe("critical");
    expect(result.isCompliant).toBe(false);
  });

  it("marque un mot de passe fort comme conforme", () => {
    const result = analyzeAnssi("K7#mPzq2Xrw!");
    expect(result.isCompliant).toBe(true);
    expect(result.score).toBe(100);
  });

  it("détecte une suite évidente", () => {
    const result = analyzeAnssi("Abcdefgh1234!");
    const rule = result.rules.find((r) => r.code === "no_sequence");
    expect(rule?.passed).toBe(false);
  });

  it("détecte un caractère répété 4 fois ou plus", () => {
    const result = analyzeAnssi("Aaaaaaaa1234!");
    const rule = result.rules.find((r) => r.code === "no_repeat");
    expect(rule?.passed).toBe(false);
  });

  it("autorise 3 caractères répétés consécutifs", () => {
    const result = analyzeAnssi("Aaa1#zzzB234!");
    const rule = result.rules.find((r) => r.code === "no_repeat");
    expect(rule?.passed).toBe(true);
  });

  it("vérifie la limite de longueur minimale", () => {
    const justShort = analyzeAnssi("Ab3#Ab3#Ab3");
    const exactlyMin = analyzeAnssi("Ab3#Ab3#Ab34");
    expect(justShort.rules.find((r) => r.code === "min_length")?.passed).toBe(false);
    expect(exactlyMin.rules.find((r) => r.code === "min_length")?.passed).toBe(true);
  });
});
