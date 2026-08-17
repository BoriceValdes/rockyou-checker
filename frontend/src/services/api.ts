const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

interface SuffixMatchDto {
  hash_suffix: string;
  occurrence_count: number;
}

interface BreachCheckResponseDto {
  hash_prefix: string;
  matches: SuffixMatchDto[];
}

export class ApiError extends Error {}

/**
 * Interroge le backend avec uniquement le PRÉFIXE (5 caractères) du hash
 * SHA-1 du mot de passe. Le serveur ne reçoit jamais le mot de passe, ni
 * le hash complet : voir README, section "Modèle de confidentialité".
 */
export async function fetchSuffixesForPrefix(prefix: string): Promise<SuffixMatchDto[]> {
  const response = await fetch(`${API_BASE}/breach-check`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ hash_prefix: prefix }),
  });

  if (response.status === 429) {
    throw new ApiError("Trop de requêtes envoyées. Merci de patienter quelques instants.");
  }
  if (!response.ok) {
    throw new ApiError("Le service de vérification est momentanément indisponible.");
  }

  const data: BreachCheckResponseDto = await response.json();
  return data.matches;
}
