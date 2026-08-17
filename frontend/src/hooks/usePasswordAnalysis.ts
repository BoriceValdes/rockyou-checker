import { useCallback, useState } from "react";
import { analyzeAnssi } from "../services/anssi";
import { ApiError, fetchSuffixesForPrefix } from "../services/api";
import { sha1Hex, splitHash } from "../services/crypto";
import type { PasswordAnalysis } from "../types/domain";

interface State {
  loading: boolean;
  error: string | null;
  result: PasswordAnalysis | null;
}

export function usePasswordAnalysis() {
  const [state, setState] = useState<State>({ loading: false, error: null, result: null });

  const analyze = useCallback(async (password: string) => {
    if (!password) {
      setState({ loading: false, error: "Merci de saisir un mot de passe.", result: null });
      return;
    }

    setState({ loading: true, error: null, result: null });

    try {
      // 1. Analyse ANSSI : purement locale, aucun octet transmis.
      const anssi = analyzeAnssi(password);

      // 2. Vérification de compromission via k-anonymat : seul un
      //    préfixe de 5 caractères du SHA-1 quitte le navigateur.
      const digest = await sha1Hex(password);
      const { prefix, suffix } = splitHash(digest);
      const matches = await fetchSuffixesForPrefix(prefix);
      const found = matches.find((m) => m.hash_suffix === suffix);

      setState({
        loading: false,
        error: null,
        result: {
          anssi,
          breach: {
            isCompromised: Boolean(found),
            occurrenceCount: found?.occurrence_count ?? 0,
          },
        },
      });
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Une erreur inattendue est survenue.";
      setState({ loading: false, error: message, result: null });
    }
  }, []);

  const reset = useCallback(() => setState({ loading: false, error: null, result: null }), []);

  return { ...state, analyze, reset };
}
