from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

# Limite le nombre de requêtes par IP. Même si aucune donnée sensible
# n'est exposée par l'API, ceci évite l'énumération massive de préfixes
# et les abus de ressources sur la base de données.
limiter = Limiter(key_func=get_remote_address) 
