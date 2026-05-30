from typing import List, Dict, Any
from utils.schema import CourseRecord, CrawlResult
from verifier.semantic_verifier import SemanticVerifier
from verifier.duplicate_checker import detect_duplicates
from utils.logger import logger

class IntegrityChecker:
    def __init__(self):
        self.semantic_verifier = SemanticVerifier()
        self.duplicates_cache = {}

    def preload_dataset(self, records: List[CourseRecord]):
        """Preloads all records to run dataset-wide rule checks like duplicates."""
        self.duplicates_cache = detect_duplicates(records)

    def check_integrity(self, dataset: CourseRecord, web_data: CrawlResult) -> Dict[str, Any]:
        """
        Stage 1: Rule-based Checks (Duplicates)
        Stage 2/3: Semantic Verification & ML Prediction
        """
        # 1. Check for duplicates
        duplicate_warning = self.duplicates_cache.get(dataset.row_number)
        
        # 2. Run Semantic & ML Verification
        result = self.semantic_verifier.verify(dataset, web_data)
        
        if duplicate_warning:
            result['suggested_correction'] = result.get('suggested_correction') or {}
            result['suggested_correction']['duplicate_warning'] = duplicate_warning
            # Downgrade status if it's a duplicate and valid
            if result['status'] == "VALID":
                result['status'] = "PARTIAL_MATCH"
                
        return result
