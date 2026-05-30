from typing import Dict, Any
from utils.schema import CourseRecord, CrawlResult
from extractor.web_extractor import WebExtractor
from ml.feature_engineering import FeatureEngineer
from ml.classifier import VerificationClassifier
from taxonomy.mapper import TaxonomyMapper

class SemanticVerifier:
    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        self.classifier = VerificationClassifier()
        self.taxonomy = TaxonomyMapper()

    def verify(self, dataset: CourseRecord, web_data: CrawlResult) -> Dict[str, Any]:
        """
        Runs the full ML-based verification pipeline.
        Returns a dictionary containing the status, confidence, features, and taxonomy suggestions.
        """
        # 1. Extract raw heuristics
        extractor = WebExtractor(web_data.extracted_text or "")
        web_extracted = extractor.extract_all()

        # 2. Generate ML Features
        features = self.feature_engineer.generate_features(dataset, web_data, web_extracted)

        # 3. Classify Integrity
        label, confidence = self.classifier.predict(features)

        # 4. Taxonomy check
        suggested_correction = None
        if label != "BROKEN_LINK":
            pred_domain, pred_subdomain, tax_conf = self.taxonomy.classify_text(web_extracted.get('text', ''))
            suggested_correction = self.taxonomy.suggest_correction(dataset.field_domain, pred_domain, tax_conf)

        return {
            "status": label,
            "confidence": confidence,
            "features": features,
            "suggested_correction": suggested_correction,
            "web_extracted": web_extracted
        }
