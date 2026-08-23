const API_BASE = import.meta.env.VITE_API_BASE_URL;

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
