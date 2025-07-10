// Flutter Integration Example - Documentation
// How to integrate Elephas AI scam detection into Flutter apps

/*
STEP 1: Add dependencies to your Flutter app's pubspec.yaml

dependencies:
  http: ^1.1.0
  provider: ^6.1.1

STEP 2: Create API service in your Flutter app
File: lib/services/elephas_api_service.dart
*/

/*
import 'dart:convert';
import 'package:http/http.dart' as http;

class ElephasApiService {
  // Your live API URL
  static const String baseUrl = 'https://elephas-ai-api.onrender.com';
  
  // API endpoints
  static const String scanEndpoint = '$baseUrl/scan';
  static const String healthEndpoint = '$baseUrl/health';
  static const String statsEndpoint = '$baseUrl/api/stats';
  
  // Scam detection with your API
  static Future<Map<String, dynamic>> scanMessage({
    required String text,
    String? sender,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(scanEndpoint),
        headers: {
          'Content-Type': 'application/json',
        },
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
  
  // ✅ Real-time health monitoring
  static Future<bool> isApiHealthy() async {
    try {
      final response = await http.get(Uri.parse(healthEndpoint));
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
  
  // ✅ Dashboard data for Flutter
  static Future<Map<String, dynamic>> getDashboardStats() async {
    final response = await http.get(Uri.parse(statsEndpoint));
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Failed to fetch dashboard stats');
  }
}
