import requests
import json
from datetime import datetime

def test_elephas_ai_api():
    """Test the Elephas AI API with various scam examples"""
    
    base_url = "http://localhost:8000/api/v1"
    
    test_messages = [
        {
            "message": "Congratulations! You've won $1,000,000! Click here immediately to claim your prize before it expires!",
            "sender": "noreply@winner-alert.com",
            "message_type": "email",
            "expected_risk": "HIGH"
        },
        {
            "message": "Your bank account has been suspended. Verify your account immediately by clicking this link: http://secure-bank-update.com",
            "sender": "security@bank-alert.net",
            "message_type": "sms",
            "expected_risk": "CRITICAL"
        },
        {
            "message": "Hi mom, can you pick up some groceries on your way home? Thanks!",
            "sender": "family_member",
            "message_type": "sms",
            "expected_risk": "MINIMAL"
        },
        {
            "message": "URGENT: Your payment of $299 is due TODAY! Call 1-800-SCAM-NOW to avoid penalties!",
            "sender": "1234567890",
            "message_type": "call",
            "expected_risk": "HIGH"
        }
    ]
    
    print("� Testing Elephas AI")
    print("=" * 50)
    
    for i, test in enumerate(test_messages, 1):
        print(f"\n📝 Test {i}: {test['expected_risk']} Risk Expected")
        print(f"Message: {test['message'][:60]}...")
        
        try:
            response = requests.post(f"{base_url}/scan", json=test)
            if response.status_code == 200:
                result = response.json()
                risk_score = result['risk_score']
                risk_level = result['risk_level']
                explanation = result['explanation']
                
                print(f"✅ Risk Score: {risk_score:.3f}")
                print(f"✅ Risk Level: {risk_level}")
                print(f"✅ Explanation: {explanation}")
                print(f"✅ Processing Time: {result['processing_time_ms']:.1f}ms")
                
                # Check if prediction matches expectation
                expected_high_risk = test['expected_risk'] in ['HIGH', 'CRITICAL']
                actual_high_risk = risk_score > 0.6
                
                if expected_high_risk == actual_high_risk:
                    print("🎯 Prediction matches expectation!")
                else:
                    print("⚠️  Prediction differs from expectation")
                    
            else:
                print(f"❌ API Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    # Test batch processing
    print(f"\n📦 Testing Batch Processing...")
    batch_request = {"messages": test_messages}
    
    try:
        response = requests.post(f"{base_url}/batch-scan", json=batch_request)
        if response.status_code == 200:
            result = response.json()
            summary = result['summary']
            print(f"✅ Batch processed: {summary['total_processed']} messages")
            print(f"✅ Scams detected: {summary['scam_detected']}")
            print(f"✅ Risk distribution: {summary['risk_distribution']}")
            print(f"✅ Avg processing time: {summary['avg_processing_time']:.1f}ms")
        else:
            print(f"❌ Batch API Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Batch test failed: {e}")

if __name__ == "__main__":
    test_elephas_ai_api()