// Package hasher calcule le hash SHA-1 hexadécimal (majuscules) d'un mot
// de passe et le découpe en préfixe (5) / suffixe (35), exactement comme
// le fait le service Have I Been Pwned (modèle de k-anonymat).
//
// Note : SHA-1 est ici utilisé uniquement pour indexer un corpus de fuite
// connu (RockYou) et permettre une recherche par préfixe — ce n'est PAS
// une recommandation de hachage pour stocker des mots de passe applicatifs
// (qui doivent utiliser argon2id/bcrypt avec sel).
package hasher

import (
	"crypto/sha1" //nolint:gosec // usage volontaire, voir doc du package
	"encoding/hex"
	"strings"
)

// Digest calcule le SHA-1 hexadécimal (majuscules) d'une chaîne.
func Digest(password string) string {
	sum := sha1.Sum([]byte(password)) //nolint:gosec
	return strings.ToUpper(hex.EncodeToString(sum[:]))
}

// Split retourne (préfixe 5 caractères, suffixe 35 caractères) d'un hash SHA-1.
func Split(hexDigest string) (prefix string, suffix string) {
	if len(hexDigest) != 40 {
		return "", ""
	}
	return hexDigest[:5], hexDigest[5:]
}
