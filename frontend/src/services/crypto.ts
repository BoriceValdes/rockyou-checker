/**
 * Calcule le hash SHA-1 (hexadécimal, majuscules) d'une chaîne, en
 * utilisant exclusivement l'API Web Crypto native du navigateur.
 * Seul le préfixe (5 premiers caractères) du hash résultant sera transmis
 * au serveur - voir `services/api.ts`.
 */
export async function sha1Hex(input: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(input);
  const digest = await crypto.subtle.digest("SHA-1", data);
  const bytes = Array.from(new Uint8Array(digest));
  return bytes.map((b) => b.toString(16).padStart(2, "0")).join("").toUpperCase();
}

export function splitHash(hexDigest: string): { prefix: string; suffix: string } {
  return { prefix: hexDigest.slice(0, 5), suffix: hexDigest.slice(5) };
}
