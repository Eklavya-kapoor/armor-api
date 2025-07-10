/*
=============================================================================
ELEPHAS AI - FLUTTER INTEGRATION GUIDE
=============================================================================

This is a documentation file showing how to integrate Elephas AI scam 
detection into any Flutter application.

For the actual working implementation, see:
- /scamshield_flutter_app/ - Complete working Flutter app
- /elephas-ai-sdk/ - Enterprise dashboard
- /scamshield-ai/ - Backend API

=============================================================================
STEP 1: Add Dependencies
=============================================================================

Add to your Flutter app's pubspec.yaml:

dependencies:
  http: ^1.1.0
  provider: ^6.1.1
  permission_handler: ^11.0.1

=============================================================================
STEP 2: Create API Service
=============================================================================

File: lib/services/elephas_api_service.dart

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class ElephasApiService {
  static const String baseUrl = 'https://elephas-ai-api.onrender.com';
  static const String scanEndpoint = '$baseUrl/scan';
  static const String healthEndpoint = '$baseUrl/health';
  
  static Future<Map<String, dynamic>> scanMessage({
    required String text,
    String? sender,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(scanEndpoint),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'text': text,
          'sender': sender ?? '',
          'metadata': metadata ?? {},
        }),
      );
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('API Error: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Network Error: $e');
    }
  }
  
  static Future<bool> isApiHealthy() async {
    try {
      final response = await http.get(Uri.parse(healthEndpoint));
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
}
```

=============================================================================
STEP 3: Usage Example
=============================================================================

```dart
class MessageScanner extends StatelessWidget {
  const MessageScanner({super.key});

  Future<void> checkMessage(String message) async {
    try {
      final result = await ElephasApiService.scanMessage(
        text: message,
        sender: 'WhatsApp',
        metadata: {'source': 'chat'},
      );
      
      if (result['risk_score'] > 0.7) {
        showScamAlert(result);
      }
    } catch (e) {
      print('Scan failed: $e');
    }
  }
  
  void showScamAlert(Map<String, dynamic> result) {
    // Show your scam alert UI
    // See scamshield_flutter_app for full overlay implementation
  }
  
  @override
  Widget build(BuildContext context) {
    return YourUIHere();
  }
}
```

=============================================================================
ENTERPRISE FEATURES
=============================================================================

For enterprise clients, add API key authentication:

```dart
static Future<Map<String, dynamic>> scanMessageWithApiKey({
  required String text,
  required String apiKey,
  String? sender,
  Map<String, dynamic>? metadata,
}) async {
  final response = await http.post(
    Uri.parse(scanEndpoint),
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $apiKey',
    },
    body: json.encode({
      'text': text,
      'sender': sender ?? '',
      'metadata': metadata ?? {},
    }),
  );
  
  return json.decode(response.body);
}
```

=============================================================================
COMPLETE IMPLEMENTATION
=============================================================================

For a complete working example with:
- Real-time overlay alerts
- System-wide protection
- Enterprise dashboard
- API key management

See the full scamshield_flutter_app implementation in this repository.

=============================================================================
*/

// This is a documentation file
// For actual implementation, see scamshield_flutter_app folder
