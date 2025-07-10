#!/usr/bin/env python3
"""
Test script for the enhanced Elephas AI API
"""

import requests
import json
import time

# Test cases
test_messages = [
    {
        "text": "Congratulations! You've won $1,000,000! Click here to claim your prize now before it expires!",
        "sender": "winner@totallylegit.com",
        "expected": "high_risk"
    },
    {
        "text": "Your account has been suspended. Verify your information immediately by clicking this link.",
        "sender": "security@banknotreal.com", 
        "expected": "high_risk"
    },
    {
        "text": "Hi mom, just wanted to let you know I arrived safely at the hotel.",
        "sender": "john@gmail.com",
        "expected": "low_risk"
    },
    {
        "text": "Meeting scheduled for tomorrow at 2 PM in conference room B.",
        "sender": "colleague@company.com",
        "expected": "low_risk"
    },
    {
        "text": "URGENT! Your computer is infected with virus. Download our antivirus software now!",
        "sender": "help@virusremover.net",
        "expected": "high_risk"
    }
]

def test_api_endpoint(base_url="http://localhost:8000"):
    """Test the /scan endpoint with various messages"""
    
    print("🐘 Testing Elephas AI Enhanced API")
    print("=" * 50)
    
    # Test health endpoint first
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            health_data = response.json()
            print(f"   Status: {health_data.get('status')}")
            print(f"   Version: {health_data.get('version')}")
        else:
            print("❌ Health check failed")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False
    
    print("\n🔍 Testing scan endpoint:")
    print("-" * 30)
    
    for i, test_case in enumerate(test_messages, 1):
        try:
            # Prepare request
            scan_data = {
                "text": test_case["text"],
                "sender": test_case["sender"],
                "metadata": {}
            }
            
            print(f"\nTest {i}: {test_case['expected'].replace('_', ' ').title()}")
            print(f"Message: {test_case['text'][:50]}...")
            print(f"Sender: {test_case['sender']}")
            
            start_time = time.time()
            response = requests.post(f"{base_url}/scan", json=scan_data)
            response_time = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == 200:
                result = response.json()
                risk_score = result.get('risk_score', 0.0)
                risk_level = result.get('risk_level', 'unknown')
                classification = result.get('classification', 'unknown')
                explanation = result.get('explanation', 'No explanation')
                
                print(f"✅ Result: {risk_level.upper()} risk ({risk_score:.3f})")
                print(f"   Classification: {classification}")
                print(f"   Confidence: {result.get('confidence', 0):.2f}")
                print(f"   Processing time: {response_time}ms")
                print(f"   AI Time: {result.get('processing_time', 0)}ms")
                print(f"   Explanation: {explanation[:100]}...")
                
                # Check if result matches expectation
                if test_case["expected"] == "high_risk" and risk_score >= 0.6:
                    print("   ✅ Expected high risk detected correctly")
                elif test_case["expected"] == "low_risk" and risk_score < 0.4:
                    print("   ✅ Expected low risk detected correctly")
                else:
                    print(f"   ⚠️ Unexpected result (expected {test_case['expected']})")
                    
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Test {i} failed: {e}")
    
    print("\n🚀 Testing enhanced scan endpoint:")
    print("-" * 35)
    
    # Test enhanced scan with a complex scam message
    enhanced_test = {
        "text": "URGENT: Your bank account will be closed in 24 hours. Click here to verify your identity and prevent account closure. This is your final notice!",
        "sender": "security@yourbank-verification.com",
        "metadata": {"source": "email", "received_time": "2024-01-15T10:30:00Z"}
    }
    
    try:
        response = requests.post(f"{base_url}/scan/enhanced", json=enhanced_test)
        if response.status_code == 200:
            result = response.json()
            print("✅ Enhanced scan successful")
            print(f"   Risk Score: {result['risk_assessment']['risk_score']}")
            print(f"   Risk Level: {result['risk_assessment']['risk_level']}")
            print(f"   Classification: {result['risk_assessment']['classification']}")
            print(f"   Forensics available: {len(result.get('forensics', {}))}")
            print(f"   Recommendations: {len(result.get('recommendations', []))}")
        else:
            print(f"❌ Enhanced scan failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Enhanced scan error: {e}")
    
    print("\n📊 Testing bulk scan:")
    print("-" * 20)
    
    # Test bulk scanning
    bulk_messages = [
        {"text": msg["text"], "sender": msg["sender"], "id": f"msg_{i}"}
        for i, msg in enumerate(test_messages[:3])
    ]
    
    try:
        bulk_data = {"messages": bulk_messages, "priority": "high"}
        response = requests.post(f"{base_url}/scan/bulk", json=bulk_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Bulk scan successful")
            print(f"   Processed: {result['processed']}/{result['total_messages']}")
            print(f"   High risk detected: {result['high_risk_detected']}")
            print(f"   Processing time: {result['processing_time']}ms")
            print(f"   Summary: {result['summary']}")
        else:
            print(f"❌ Bulk scan failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Bulk scan error: {e}")
    
    print("\n🎯 Testing model info:")
    print("-" * 20)
    
    try:
        response = requests.get(f"{base_url}/model/info")
        if response.status_code == 200:
            result = response.json()
            print("✅ Model info retrieved")
            print(f"   Model: {result['model_name']}")
            print(f"   Status: {result['status']}")
            print(f"   Accuracy: {result['performance_metrics']['accuracy']}")
        else:
            print(f"❌ Model info failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Model info error: {e}")
        
    print("\n" + "=" * 50)
    print("🎉 API Testing Complete!")

if __name__ == "__main__":
    print("Starting API test...")
    test_api_endpoint()
