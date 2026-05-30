import pandas as pd
from typing import Dict, Any
from ml.embedding_engine import EmbeddingEngine
from extractor.normalizer import normalize_text, extract_numeric_fee, normalize_duration_to_months
from utils.schema import CourseRecord, CrawlResult
from taxonomy.mapper import TaxonomyMapper

class FeatureEngineer:
    def __init__(self):
        self.embedding = EmbeddingEngine()
        self.taxonomy = TaxonomyMapper()

    def generate_features(self, dataset: CourseRecord, web_data: CrawlResult, web_extracted: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates ML features comparing the dataset to the extracted web data.
        Returns a dictionary of features suitable for XGBoost/LightGBM inference.
        """
        features = {}
        
        # Base boolean flags
        features['broken_link'] = 1 if web_data.status_code and web_data.status_code >= 400 else 0
        features['redirect_detected'] = 1 if web_data.final_url and str(dataset.link) not in web_data.final_url else 0
        features['page_length'] = len(web_extracted.get('text', ''))
        features['response_time'] = web_data.response_time_ms or 0.0

        if features['broken_link']:
            # Return zeros for the rest if broken link
            self._fill_zeros(features)
            return features

        # 1. Text Similarity Features
        web_text = web_extracted.get('text', '')
        features['course_name_similarity'] = self.embedding.compute_similarity(dataset.course_name, web_text)
        features['institute_similarity'] = self.embedding.compute_similarity(dataset.institute_name, web_text)
        features['description_similarity'] = self.embedding.compute_similarity(dataset.description, web_text)
        
        # 2. Numeric Difference Features
        dataset_fee = extract_numeric_fee(dataset.fees)
        web_fee = extract_numeric_fee(web_extracted.get('fees_extracted'))
        features['fees_difference'] = abs(dataset_fee - web_fee) if web_fee > 0 else -1 # -1 implies missing on web

        dataset_dur = normalize_duration_to_months(dataset.duration)
        web_dur = normalize_duration_to_months(web_extracted.get('duration_extracted'))
        features['duration_difference'] = abs(dataset_dur - web_dur) if web_dur > 0 else -1

        # 3. Taxonomy & Domain Features
        domain, subdomain, tax_conf = self.taxonomy.classify_text(web_text, dataset.field_domain)
        features['predicted_domain_conf'] = tax_conf
        features['domain_match'] = 1 if normalize_text(dataset.field_domain) in normalize_text(domain) else 0
        features['course_type_similarity'] = self.embedding.compute_similarity(dataset.course_type, web_text)
        
        # 4. Boolean Features
        features['scholarship_detected'] = 1 if web_extracted.get('has_scholarship') else 0
        features['certificate_exists'] = 1 if web_extracted.get('has_certificate') else 0
        
        return features

    def _fill_zeros(self, features: Dict[str, Any]):
        keys = [
            'course_name_similarity', 'institute_similarity', 'description_similarity',
            'fees_difference', 'duration_difference', 'predicted_domain_conf', 
            'domain_match', 'course_type_similarity', 'scholarship_detected', 'certificate_exists'
        ]
        for k in keys:
            features[k] = 0.0
