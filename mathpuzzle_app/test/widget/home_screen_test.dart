import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:mathpuzzle_app/screens/home_screen.dart';
import 'package:mathpuzzle_app/providers/game_provider.dart';
import 'package:mathpuzzle_app/providers/multiplayer_provider.dart';
import '../mocks.dart';

void main() {
  late MockApiService mockApiService;
  late MockWebSocketService mockWebSocketService;

  setUp(() {
    mockApiService = MockApiService();
    mockWebSocketService = MockWebSocketService();
  });

  Widget createHomeScreen() {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => GameProvider(apiService: mockApiService, webSocketService: mockWebSocketService)),
        ChangeNotifierProvider(create: (_) => MultiplayerProvider(apiService: mockApiService, webSocketService: mockWebSocketService)),
      ],
      child: MaterialApp(
        home: HomeScreen(apiService: mockApiService, baseUrl: 'http://localhost'),
      ),
    );
  }

  group('HomeScreen Widget Tests', () {
    testWidgets('Renders essential UI elements', (WidgetTester tester) async {
      await tester.pumpWidget(createHomeScreen());
      await tester.pumpAndSettle();

      expect(find.text('Welcome to the Math Game!'), findsOneWidget);
      expect(find.text('Start New Game'), findsOneWidget);
      expect(find.text('Enter your GamerId:'), findsOneWidget);
      expect(find.text('Game Type:'), findsOneWidget);
      expect(find.text('Category:'), findsOneWidget);
      expect(find.text('Difficulty:'), findsOneWidget);
      expect(find.text('Start Single Player Game'), findsOneWidget);
    });

    testWidgets('Toggles between Single and Multi game types', (WidgetTester tester) async {
      await tester.pumpWidget(createHomeScreen());
      await tester.pumpAndSettle();

      // Initially 'Single' is selected
      expect(find.text('Start Single Player Game'), findsOneWidget);

      // Tap 'Multi' radio button
      await tester.tap(find.text('Multi'));
      await tester.pumpAndSettle();

      expect(find.text('Create Multiplayer Lobby'), findsOneWidget);
    });

    testWidgets('Displays Join Active Lobby section', (WidgetTester tester) async {
      await tester.pumpWidget(createHomeScreen());
      await tester.pumpAndSettle();

      expect(find.text('Join Active Lobby'), findsOneWidget);
      expect(find.text('Enter Room ID manually:'), findsOneWidget);
      
      // Since mock returns 1 room, it should be visible
      expect(find.text('Room: room1'), findsOneWidget);
      expect(find.text('Creator: Host1 | 1 players | algebra (medium)'), findsOneWidget);
    });
  });
}
