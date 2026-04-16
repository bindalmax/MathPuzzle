import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'services/api_service.dart';
import 'services/websocket_service.dart';
import 'providers/game_provider.dart';
import 'providers/multiplayer_provider.dart';
import 'screens/home_screen.dart';

void main() {
  const String apiBaseUrl = 'http://127.0.0.1:5000';
  final apiService = ApiService(apiBaseUrl);
  final webSocketService = WebSocketService(apiBaseUrl.replaceFirst('http', 'ws'));
  webSocketService.connect();

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => GameProvider(apiService: apiService)),
        ChangeNotifierProvider(create: (_) => MultiplayerProvider(webSocketService: webSocketService)),
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
      theme: ThemeData(primarySwatch: Colors.blue),
      home: HomeScreen(apiService: apiService, baseUrl: baseUrl),
    );
  }
}
