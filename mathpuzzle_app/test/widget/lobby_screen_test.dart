import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:mathpuzzle_app/screens/lobby_screen.dart';
import 'package:mathpuzzle_app/screens/game_screen.dart';
import 'package:mathpuzzle_app/providers/game_provider.dart';
import 'package:mathpuzzle_app/providers/multiplayer_provider.dart';
import 'package:mathpuzzle_app/providers/auth_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../mocks.dart';

void main() {
  late MockApiService mockApiService;
  late MockWebSocketService mockWebSocketService;

  setUp(() {
    SharedPreferences.setMockInitialValues({});
    mockApiService = MockApiService();
    mockWebSocketService = MockWebSocketService();
  });

  Widget createLobbyScreen() {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider(apiService: mockApiService, googleSignIn: MockGoogleSignIn())),
        ChangeNotifierProvider(create: (_) => GameProvider(apiService: mockApiService, webSocketService: mockWebSocketService)),
        ChangeNotifierProvider(create: (_) => MultiplayerProvider(apiService: mockApiService, webSocketService: mockWebSocketService)),
      ],
      child: const MaterialApp(
        home: LobbyScreen(
          category: 'percentage',
          difficulty: 'medium',
          mode: 'time',
          modeValue: 20,
        ),
      ),
    );
  }

  group('LobbyScreen Widget Tests', () {
    testWidgets('Renders essential UI elements', (WidgetTester tester) async {
      await tester.pumpWidget(createLobbyScreen());
      
      expect(find.text('Multiplayer Lobby'), findsOneWidget);
      expect(find.text('Room ID'), findsOneWidget);
      expect(find.text('Current Players:'), findsOneWidget);
      expect(find.text('Leave Lobby'), findsOneWidget);
    });

    testWidgets('Shows Start Game button only for host', (WidgetTester tester) async {
      final mpProvider = MultiplayerProvider(apiService: mockApiService, webSocketService: mockWebSocketService);
      
      // Initially not host
      await tester.pumpWidget(
        MultiProvider(
          providers: [
            ChangeNotifierProvider(create: (_) => AuthProvider(apiService: mockApiService, googleSignIn: MockGoogleSignIn())),
            ChangeNotifierProvider(create: (_) => GameProvider(apiService: mockApiService)),
            ChangeNotifierProvider.value(value: mpProvider),
          ],
          child: const MaterialApp(
            home: LobbyScreen(category: 'a', difficulty: 'b', mode: 'c', modeValue: 1),
          ),
        )
      );
      
      expect(find.text('Start Game for Everyone'), findsNothing);
      expect(find.text('Waiting for host to start...'), findsOneWidget);

      // Make host
      await mpProvider.createRoom('Host', 'basic', 'easy');
      await tester.pump();
      
      expect(find.text('Start Game for Everyone'), findsOneWidget);
      expect(find.text('Waiting for host to start...'), findsNothing);
    });

    testWidgets('Navigates to GameScreen on game_start_signal', (WidgetTester tester) async {
      final mpProvider = MultiplayerProvider(apiService: mockApiService, webSocketService: mockWebSocketService);
      
      await tester.pumpWidget(
        MultiProvider(
          providers: [
            ChangeNotifierProvider(create: (_) => AuthProvider(apiService: mockApiService, googleSignIn: MockGoogleSignIn())),
            ChangeNotifierProvider(create: (_) => GameProvider(apiService: mockApiService)),
            ChangeNotifierProvider.value(value: mpProvider),
          ],
          child: const MaterialApp(
            home: LobbyScreen(category: 'percentage', difficulty: 'medium', mode: 'time', modeValue: 20),
          ),
        )
      );

      // Simulate signal
      mockWebSocketService.triggerEvent('game_start_signal', {'room': 'test'});
      await tester.pump(); // Start navigation
      await tester.pump(const Duration(milliseconds: 100)); // Process navigation
      await tester.pumpAndSettle();

      // Check if GameScreen is rendered
      expect(find.byType(GameScreen), findsOneWidget);
    });
  });
}
