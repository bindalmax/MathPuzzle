import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:mathpuzzle_app/screens/game_screen.dart';
import 'package:mathpuzzle_app/providers/game_provider.dart';
import 'package:mathpuzzle_app/providers/multiplayer_provider.dart';
import 'package:mathpuzzle_app/providers/auth_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../mocks.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  late MockApiService mockApiService;
  late MockWebSocketService mockWebSocketService;

  setUp(() {
    SharedPreferences.setMockInitialValues({});
    mockApiService = MockApiService();
    mockWebSocketService = MockWebSocketService();
  });

  Widget createGameScreen() {
    final gameProvider = GameProvider(apiService: mockApiService, webSocketService: mockWebSocketService);
    final mpProvider = MultiplayerProvider(apiService: mockApiService, webSocketService: mockWebSocketService);
    final authProvider = AuthProvider(apiService: mockApiService, googleSignIn: MockGoogleSignIn());

    return MultiProvider(
      providers: [
        ChangeNotifierProvider.value(value: authProvider),
        ChangeNotifierProvider.value(value: gameProvider),
        ChangeNotifierProvider.value(value: mpProvider),
      ],
      child: const MaterialApp(
        home: GameScreen(
          category: 'basic_arithmetic',
          difficulty: 'easy',
          playerName: 'TestUser',
          mode: 'questions',
          modeValue: 1,
        ),
      ),
    );
  }

  group('GameScreen Widget Tests', () {
    testWidgets('Restart Session button resets the game', (WidgetTester tester) async {
      await tester.pumpWidget(createGameScreen());
      await tester.pumpAndSettle();

      final gameProvider = tester.element(find.byType(GameScreen)).read<GameProvider>();

      // 1. Complete the game
      gameProvider.submitAnswer('4', 'basic', 'easy', 'TestUser');
      await tester.pump(); 
      await tester.pump(const Duration(milliseconds: 600)); // Wait for feedback delay
      await tester.pumpAndSettle();

      expect(find.text('Game Over!'), findsOneWidget);
      expect(find.text('Your Score: 1'), findsOneWidget);

      // 2. Tap Restart Session
      await tester.tap(find.text('Restart Session'));
      await tester.pump();
      await tester.pumpAndSettle();

      // 3. Verify state is reset
      expect(find.text('Score: '), findsOneWidget);
      expect(find.text('1'), findsNothing); // Score should be 0, not 1
      expect(gameProvider.score, 0);
      expect(gameProvider.isGameOver, false);
    });
  });
}
