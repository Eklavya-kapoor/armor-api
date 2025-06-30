# scamshield/deployment/mobile_config.py
from typing import Dict

class MobileDeploymentConfig:
    """Configuration for mobile deployment"""

    # Model optimization settings
    ENABLE_QUANTIZATION = True
    ENABLE_ONNX_CONVERSION = True
    MAX_SEQUENCE_LENGTH = 128  # Shorter for mobile
    BATCH_SIZE = 1  # Single message processing

    # Performance settings
    MAX_PROCESSING_TIME_MS = 200  # Maximum allowed processing time
    MEMORY_LIMIT_MB = 512  # Memory limit for model

    # Feature extraction settings
    ENABLE_ADVANCED_FEATURES = True
    ENABLE_URL_ANALYSIS = True
    ENABLE_LINGUISTIC_ANALYSIS = False  # Disable for speed

    # Alert settings
    CRITICAL_THRESHOLD = 0.8
    WARNING_THRESHOLD = 0.5
    AUTO_BLOCK_THRESHOLD = 0.9

    # Platform-specific settings
    ANDROID_SETTINGS = {
        'notification_channel': 'scamshield_alerts',
        'background_processing': True,
        'accessibility_service': True,
        'notification_listener': True
    }

    IOS_SETTINGS = {
        'app_extension': True,
        'siri_shortcuts': True,
        'notification_service': True,
        'limited_mode': True  # Due to iOS restrictions
    }

    @classmethod
    def get_mobile_config(cls, platform: str) -> Dict:
        """Get platform-specific configuration"""
        base_config = {
            'model_optimization': {
                'quantization': cls.ENABLE_QUANTIZATION,
                'onnx_conversion': cls.ENABLE_ONNX_CONVERSION,
                'max_sequence_length': cls.MAX_SEQUENCE_LENGTH
            },
            'performance': {
                'max_processing_time_ms': cls.MAX_PROCESSING_TIME_MS,
                'memory_limit_mb': cls.MEMORY_LIMIT_MB
            },
            'thresholds': {
                'critical': cls.CRITICAL_THRESHOLD,
                'warning': cls.WARNING_THRESHOLD,
                'auto_block': cls.AUTO_BLOCK_THRESHOLD
            }
        }

        if platform.lower() == 'android':
            base_config['platform'] = cls.ANDROID_SETTINGS
        elif platform.lower() == 'ios':
            base_config['platform'] = cls.IOS_SETTINGS

        return base_config
