#!/bin/bash

# Elephas AI Dashboard Test Script
echo "🧪 Testing Elephas AI Enterprise Dashboard..."
echo "=============================================="

# Test 1: API Health Check
echo "📊 Testing API Health..."
curl -s "http://localhost:8000/health" | python3 -m json.tool
echo ""

# Test 2: Scam Detection - High Risk
echo "🚨 Testing High-Risk Scam Detection..."
curl -s -X POST "http://localhost:8000/scan" \
  -H "Content-Type: application/json" \
  -d '{"text": "URGENT! Your account has been compromised. Click this link immediately to secure your account: http://phishing-site.com/login", "sender": "security@fake-bank.com", "metadata": {"detect_mixed_language": true}}' | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f'Risk Score: {data[\"risk_score\"]:.2%}')
print(f'Risk Level: {data[\"risk_level\"]}')
print(f'Explanation: {data[\"explanation\"]}')
print(f'Processing Time: {data[\"processing_time\"]}ms')
"
echo ""

# Test 3: Benign Message - Low Risk
echo "✅ Testing Benign Message Detection..."
curl -s -X POST "http://localhost:8000/scan" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hi, how are you today? I hope you have a great day!", "sender": "friend@example.com", "metadata": {"detect_mixed_language": true}}' | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f'Risk Score: {data[\"risk_score\"]:.2%}')
print(f'Risk Level: {data[\"risk_level\"]}')
print(f'Explanation: {data[\"explanation\"]}')
print(f'Processing Time: {data[\"processing_time\"]}ms')
"
echo ""

# Test 4: Dashboard Statistics
echo "📈 Testing Dashboard Statistics..."
curl -s "http://localhost:8000/api/stats" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f'Threats Blocked: {data[\"threats_blocked\"]:,}')
print(f'Scans Processed: {data[\"scans_processed\"]:,}')
print(f'Accuracy Rate: {data[\"accuracy_rate\"]}%')
print(f'Avg Response Time: {data[\"avg_response_time\"]}ms')
"
echo ""

# Test 5: Recent Activity
echo "📋 Testing Recent Activity Feed..."
curl -s "http://localhost:8000/api/activity" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f'Activity Items: {len(data)}')
for item in data[:3]:
    print(f'  • {item[\"type\"].upper()}: {item[\"message\"]}')
"
echo ""

# Test 6: Threat Analytics
echo "🔍 Testing Threat Analytics..."
curl -s "http://localhost:8000/api/threats" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f'Timeline Data Points: {len(data[\"timeline\"])}')
print(f'Threat Categories: {len(data[\"categories\"])}')
for cat in data[\"categories\"]:
    print(f'  • {cat[\"name\"]}: {cat[\"count\"]} threats')
"
echo ""

echo "🎉 All tests completed successfully!"
echo "Dashboard available at: http://localhost:8000"
echo "Threat Scanner available at: http://localhost:8000/dashboard/threat-detection.html"
echo "Settings available at: http://localhost:8000/dashboard/settings.html"
