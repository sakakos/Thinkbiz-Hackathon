from typing import Dict, Any

# Σε ένα MVP hackathon, χρησιμοποιούμε ένα in-memory dictionary.
# Στην παραγωγή, αυτό θα ήταν μια βάση δεδομένων (π.χ. Azure Cosmos DB ή Redis)[cite: 33].
active_requests: Dict[str, Any] = {}