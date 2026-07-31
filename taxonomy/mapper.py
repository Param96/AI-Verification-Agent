from typing import Tuple, Dict
from ml.embedding_engine import EmbeddingEngine
from taxonomy.definitions import CYBERSECURITY_TAXONOMY, get_all_subdomains
from utils.logger import logger


class TaxonomyMapper:
    def __init__(self):
        self.engine = EmbeddingEngine()
        self.subdomains = get_all_subdomains()

    def classify_text(
        self, text: str, dataset_domain: str = None
    ) -> Tuple[str, str, float]:
        """
        Classifies extracted web text into a primary domain and subdomain.
        If dataset_domain is provided and is not Cybersecurity, dynamically scores against it.
        """
        if not text:
            return "Unknown", "Unknown", 0.0

        best_score = -1.0
        best_sub = "Unknown"
        best_domain = "Unknown"

        # 1. Dynamic Domain matching
        if dataset_domain and dataset_domain.lower() != "cybersecurity":
            score = self.engine.compute_similarity(dataset_domain, text[:2000])
            if score > 0.4:  # Threshold for custom domain
                return dataset_domain, "Custom", score

        # 2. Fallback to known taxonomy
        for domain, sub_list in CYBERSECURITY_TAXONOMY.items():
            for sub in sub_list:
                score = self.engine.compute_similarity(
                    sub, text[:2000]
                )  # Truncate text for performance
                if score > best_score:
                    best_score = score
                    best_sub = sub
                    best_domain = domain

        return best_domain, best_sub, best_score

    def suggest_correction(
        self, dataset_domain: str, web_domain: str, score: float
    ) -> Dict[str, str]:
        """
        Suggests an auto-correction if the dataset domain differs from the semantically verified web domain.
        """
        if not dataset_domain:
            return {"suggestion": web_domain, "reason": "Missing in dataset"}

        if dataset_domain != web_domain and score > 0.6:
            return {
                "suggestion": web_domain,
                "reason": f"Webpage semantically matches '{web_domain}' with {score:.2f} confidence.",
            }
        return None
