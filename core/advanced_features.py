import re
import urllib.parse
from typing import Dict, List, Set
import math

class AdvancedScamFeatureExtractor:
    def __init__(self):
        """Initialize with comprehensive scam patterns"""
        self.scam_keywords = {
            'urgency': ['urgent', 'immediately', 'expires', 'limited time', 'act now', 'hurry'],
            'money': ['prize', 'winner', 'free', 'cash', 'reward', 'million', 'inheritance', '$', '£', '€'],
            'trust': ['government', 'bank', 'official', 'verify', 'confirm', 'security'],
            'action': ['click', 'download', 'install', 'call now', 'reply', 'forward'],
            'threats': ['suspended', 'blocked', 'fraud', 'unauthorized', 'violation', 'penalty'],
            'personal': ['ssn', 'social security', 'credit card', 'password', 'pin', 'account number']
        }
        
        self.suspicious_domains = {
            'bit.ly', 'tinyurl.com', 'goo.gl', 't.co',  # URL shorteners
            'secure-bank-update.com', 'verify-account.net'  # Common scam patterns
        }
        
        # Regex patterns
        self.phone_pattern = re.compile(r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})')
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        
    def extract(self, text: str, sender: str = "", metadata: Dict = None) -> Dict:
        """Extract comprehensive features from message"""
        text_lower = text.lower()
        features = {}
        
        # Basic text features
        features.update(self._extract_basic_features(text, text_lower))
        
        # Content analysis features
        features.update(self._extract_content_features(text, text_lower))
        
        # Linguistic features
        features.update(self._extract_linguistic_features(text, text_lower))
        
        # Sender analysis
        features.update(self._extract_sender_features(sender))
        
        # Metadata features
        if metadata:
            features.update(self._extract_metadata_features(metadata))
            
        return features
    
    def _extract_basic_features(self, text: str, text_lower: str) -> Dict:
        """Extract basic text statistics"""
        return {
            'length': len(text),
            'word_count': len(text.split()),
            'char_count': len(text),
            'uppercase_ratio': sum(1 for c in text if c.isupper()) / max(len(text), 1),
            'digit_ratio': sum(1 for c in text if c.isdigit()) / max(len(text), 1),
            'punctuation_count': sum(1 for c in text if c in '!@#$%^&*()'),
            'exclamation_count': text.count('!'),
            'question_count': text.count('?')
        }
    
    def _extract_content_features(self, text: str, text_lower: str) -> Dict:
        """Extract content-based features"""
        features = {}
        
        # Keyword analysis
        for category, keywords in self.scam_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            features[f'{category}_keywords'] = count
            features[f'has_{category}_keywords'] = count > 0
        
        # URL analysis
        urls = self.url_pattern.findall(text)
        features['url_count'] = len(urls)
        features['has_urls'] = len(urls) > 0
        
        suspicious_url_count = 0
        for url in urls:
            try:
                domain = urllib.parse.urlparse(url).netloc.lower()
                if any(sus_domain in domain for sus_domain in self.suspicious_domains):
                    suspicious_url_count += 1
            except:
                pass
        features['suspicious_url_count'] = suspicious_url_count
        
        # Contact information
        phones = self.phone_pattern.findall(text)
        emails = self.email_pattern.findall(text)
        features['phone_count'] = len(phones)
        features['email_count'] = len(emails)
        features['has_contact_info'] = len(phones) > 0 or len(emails) > 0
        
        # Spelling and grammar (basic)
        words = text_lower.split()
        if words:
            avg_word_length = sum(len(word) for word in words) / len(words)
            features['avg_word_length'] = avg_word_length
            features['long_words_ratio'] = sum(1 for word in words if len(word) > 8) / len(words)
        
        return features
    
    def _extract_linguistic_features(self, text: str, text_lower: str) -> Dict:
        """Extract linguistic patterns"""
        sentences = text.split('.')
        return {
            'sentence_count': len([s for s in sentences if s.strip()]),
            'avg_sentence_length': len(text.split()) / max(len(sentences), 1),
            'caps_lock_words': len([word for word in text.split() if word.isupper() and len(word) > 2]),
            'repeated_chars': len(re.findall(r'(.)\1{2,}', text_lower)),
            'numbers_in_text': len(re.findall(r'\d+', text)),
            'currency_symbols': text.count('$') + text.count('£') + text.count('€'),
        }
    
    def _extract_sender_features(self, sender: str) -> Dict:
        """Extract sender-based features"""
        if not sender:
            return {'sender_analysis': 0}
            
        sender_lower = sender.lower()
        return {
            'sender_length': len(sender),
            'sender_has_numbers': any(c.isdigit() for c in sender),
            'sender_suspicious': any(term in sender_lower for term in ['noreply', 'donotreply', 'alert', 'security']),
            'sender_is_email': '@' in sender,
            'sender_is_phone': sender.replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit()
        }
    
    def _extract_metadata_features(self, metadata: Dict) -> Dict:
        """Extract metadata-based features"""
        return {
            'time_of_day': metadata.get('hour', 12),
            'is_weekend': metadata.get('is_weekend', False),
            'is_night_time': metadata.get('hour', 12) < 6 or metadata.get('hour', 12) > 22,
            'message_type': metadata.get('type', 'unknown'),  # 'sms', 'email', 'call', etc.
        }
