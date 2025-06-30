
# scamshield/core/enhanced_scorer.py
from typing import Dict, List, Tuple
import numpy as np
import logging

from core.bert_classifier import BertScamClassifier

class EnhancedScamRiskScorer:
    def __init__(self, bert_classifier: BertScamClassifier):
        """Initialize with BERT classifier and rule-based scoring"""
        self.bert_classifier = bert_classifier
        self.feature_weights = self._initialize_weights()
        
    def _initialize_weights(self) -> Dict[str, float]:
        """Initialize feature weights based on scam analysis"""
        return {
            # High-risk indicators
            'personal_keywords': 0.8,
            'threats_keywords': 0.7,
            'urgency_keywords': 0.6,
            'suspicious_url_count': 0.9,
            'has_urls': 0.4,
            
            # Medium-risk indicators
            'money_keywords': 0.5,
            'action_keywords': 0.4,
            'trust_keywords': 0.3,
            'has_contact_info': 0.3,
            
            # Text pattern risks
            'uppercase_ratio': 0.3,
            'exclamation_count': 0.2,
            'sender_suspicious': 0.6,
            'is_night_time': 0.2,
            
            # Protective factors (negative weights)
            'sender_is_email': -0.1,
            'sentence_count': -0.05,
        }
    
    def score(self, text: str, features: Dict, sender: str = "") -> Tuple[float, str, Dict]:
        """
        Calculate comprehensive risk score using ensemble method
        Returns: (risk_score, explanation, detailed_analysis)
        """
        # Get BERT prediction
        bert_score, bert_confidence = self.bert_classifier.predict(text)
        
        # Calculate rule-based score
        rule_score, rule_explanation = self._calculate_rule_score(features)
        
        # Ensemble scoring (weighted combination)
        bert_weight = 0.7  # BERT gets higher weight as it's trained on data
        rule_weight = 0.3
        
        final_score = (bert_score * bert_weight) + (rule_score * rule_weight)
        final_score = min(max(final_score, 0.0), 1.0)  # Clamp to [0,1]
        
        # Generate explanation
        explanation = self._generate_explanation(
            final_score, bert_score, rule_score, rule_explanation, features
        )
        
        # Detailed analysis for debugging/transparency
        detailed_analysis = {
            'bert_score': bert_score,
            'bert_confidence': bert_confidence,
            'rule_score': rule_score,
            'final_score': final_score,
            'risk_level': self._get_risk_level(final_score),
            'top_risk_factors': self._get_top_risk_factors(features)
        }
        
        return final_score, explanation, detailed_analysis
    
    def _calculate_rule_score(self, features: Dict) -> Tuple[float, List[str]]:
        """Calculate rule-based risk score"""
        score = 0.0
        explanations = []
        
        for feature, weight in self.feature_weights.items():
            if feature in features and features[feature]:
                if isinstance(features[feature], bool):
                    contribution = weight if features[feature] else 0
                elif isinstance(features[feature], (int, float)):
                    # Normalize numeric features
                    normalized_value = min(features[feature] / 10.0, 1.0)
                    contribution = weight * normalized_value
                else:
                    contribution = 0
                
                score += contribution
                
                if contribution > 0.1:  # Only explain significant contributions
                    explanations.append(f"{feature.replace('_', ' ').title()}")
        
        return min(score, 1.0), explanations
    
    def _generate_explanation(self, final_score: float, bert_score: float, 
                            rule_score: float, rule_explanation: List[str], 
                            features: Dict) -> str:
        """Generate human-readable explanation"""
        risk_level = self._get_risk_level(final_score)
        
        if final_score < 0.3:
            return f"✅ Message appears safe ({risk_level})"
        
        explanation_parts = []
        
        if bert_score > 0.6:
            explanation_parts.append("AI detected scam patterns")
        
        if rule_explanation:
            explanation_parts.extend(rule_explanation[:3])  # Top 3 rule explanations
        
        # Add specific warnings
        if features.get('suspicious_url_count', 0) > 0:
            explanation_parts.append("⚠️ Contains suspicious URLs")
        
        if features.get('personal_keywords', 0) > 0:
            explanation_parts.append("🚨 Asks for personal information")
        
        explanation = " • ".join(explanation_parts[:4])  # Limit to 4 points
        return f"🚫 {risk_level}: {explanation}"
    
    def _get_risk_level(self, score: float) -> str:
        """Convert score to risk level"""
        if score >= 0.8:
            return "CRITICAL RISK"
        elif score >= 0.6:
            return "HIGH RISK"
        elif score >= 0.4:
            return "MEDIUM RISK"
        elif score >= 0.2:
            return "LOW RISK"
        else:
            return "MINIMAL RISK"
    
    def _get_top_risk_factors(self, features: Dict) -> List[str]:
        """Get top risk factors for detailed analysis"""
        risk_factors = []
        
        high_risk_features = [
            ('suspicious_url_count', 'Suspicious URLs'),
            ('personal_keywords', 'Personal Info Requests'),
            ('threats_keywords', 'Threatening Language'),
            ('urgency_keywords', 'Urgency Tactics'),
            ('money_keywords', 'Money/Prize Claims')
        ]
        
        for feature, description in high_risk_features:
            if features.get(feature, 0) > 0:
                risk_factors.append(description)
        
        return risk_factors[:5]  # Top 5
