import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:mathpuzzle_app/screens/game_screen.dart';
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

  Widget createGameScreen(GameProvider gameProvider, MultiplayerProvider mpProvider) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider.value(value: gameProvider),
        ChangeNotifierProvider.value(value: mpProvider),
      ],
      child: const MaterialApp(
        home: GameScreen(
          category: 'basic_arithmetic',
          difficulty: 'easy',
          playerName: 'TestUser',
          isMultiplayer: true,
        ),
      ),
    );
  }

  group('Multiplayer Game End UI Tests', () {
    testWidgets('Shows other players scores when game finishes', (WidgetTester tester) async {
      final gameProvider = GameProvider(apiService: mockApiService, webSocketService: mockWebSocketService);
      final mpProvider = MultiplayerProvider(apiService: mockApiService, webSocketService: mockWebSocketService);

      // 1. Start on GameScreen
      await tester.pumpWidget(createGameScreen(gameProvider, mpProvider));
      await tester.pumpAndSettle();

      // 2. Simulate game end
      gameProvider.endGame('basic', 'easy', 'TestUser', 10.0);
      await tester.pump(); // Start transition to game over
      await tester.pump(const Duration(milliseconds: 100)); // Process state

      expect(find.text('Game Over!'), findsOneWidget);
      expect(find.text('Your Score: 0'), findsOneWidget);

      // 3. Initially might show waiting if no scores received yet
      expect(find.text('Waiting for other players...'), findsOneWidget);

      // 4. Simulate receiving scores from other players via WebSocket
      mockWebSocketService.triggerEvent('score_update', {
        'players': {
          'TestUser': 5,
          'OtherPlayer': 8,
          'ThirdPlayer': 3
        }
      });
      
      await tester.pump(); // Process state change
      await tester.pump(const Duration(milliseconds: 100)); // Handle any immediate UI updates

      // 5. Verify the leaderboard is shown with all players
      expect(find.text('Waiting for other players...'), findsNothing);
      expect(find.text('Multiplayer Results:'), findsOneWidget);
      
      expect(find.text('OtherPlayer'), findsOneWidget);
      expect(find.text('8 pts'), findsOneWidget);
      
      expect(find.text('TestUser'), findsOneWidget);
      expect(find.text('5 pts'), findsOneWidget);
      
      expect(find.text('ThirdPlayer'), findsOneWidget);
      expect(find.text('3 pts'), findsOneWidget);
    });
  });
}
