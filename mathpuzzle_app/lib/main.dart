import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'services/api_service.dart';
import 'services/websocket_service.dart';
import 'providers/game_provider.dart';
import 'providers/multiplayer_provider.dart';
import 'screens/home_screen.dart';
import 'config.dart'; // Import AppConfig

// Allows connecting to local HTTPS with self-signed certs
class MyHttpOverrides extends HttpOverrides {
  @override
  HttpClient createHttpClient(SecurityContext? context) {
    return super.createHttpClient(context)
      ..badCertificateCallback = (X509Certificate cert, String host, int port) => true;
  }
}

void main() async {
  // Global override for local development HTTPS
  if (!kReleaseMode) {
    HttpOverrides.global = MyHttpOverrides();
  }

  WidgetsFlutterBinding.ensureInitialized();

  // apiBaseUrl is externalized in lib/config.dart
  String apiBaseUrl = AppConfig.apiBaseUrl;
  
  print('App Starting...');
  print('API Base URL: $apiBaseUrl');

  final apiService = ApiService(apiBaseUrl);
  final webSocketService = WebSocketService(apiBaseUrl.replaceFirst('https', 'wss'));
  
  // Connectivity Check
  try {
    print('Testing connection to backend...');
    await apiService.getLeaderboard(limit: 1);
    print('Backend connection SUCCESS');
  } catch (e) {
    print('Backend connection FAILED: $e');
    print('Tip: Ensure Flask is running on port 5005 with HTTPS');
  }

  webSocketService.connect();

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => GameProvider(apiService: apiService)),
        ChangeNotifierProvider(create: (_) => MultiplayerProvider(webSocketService: webSocketService, apiService: apiService)),
      ],
      child: MyApp(apiService: apiService, baseUrl: apiBaseUrl),
    ),
  );
}

class MyApp extends StatelessWidget {
  final ApiService apiService;
  final String baseUrl;

  const MyApp({required this.apiService, required this.baseUrl, super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Math Puzzle',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.indigo,
        useMaterial3: true,
      ),
      home: HomeScreen(apiService: apiService, baseUrl: baseUrl),
    );
  }
}
