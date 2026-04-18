import 'package:flutter_test/flutter_test.dart';
import 'package:mathpuzzle_app/providers/game_provider.dart';
import '../mocks.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  late GameProvider gameProvider;
  late MockApiService mockApiService;

  setUp(() {
    mockApiService = MockApiService();
    gameProvider = GameProvider(apiService: mockApiService);
  });

  group('GameProvider Unit Tests (with Prefetching)', () {
    test('Initial state is correct', () {
      expect(gameProvider.score, 0);
      expect(gameProvider.questionsAttempted, 0);
      expect(gameProvider.isGameOver, false);
      expect(gameProvider.currentQuestion, null);
    });

    test('fetchQuestion fills buffer (fetches 2 questions)', () async {
      await gameProvider.fetchQuestion('basic_arithmetic', 'easy');
      expect(gameProvider.currentQuestion, isNotNull);
      // Logic internal check: buffer should be full, so another fetch shouldn't happen immediately
      expect(gameProvider.isLoading, false);
    });

    test('submitAnswer transitions to next question after delay', () async {
      await gameProvider.fetchQuestion('basic_arithmetic', 'easy');
      
      // Submit answer (starts 500ms delay)
      gameProvider.submitAnswer('4', 'basic_arithmetic', 'easy', 'TestPlayer');
      
      expect(gameProvider.lastAnswerCorrect, true);
      expect(gameProvider.score, 1);
      
      // Wait for delay and transition
      await Future.delayed(const Duration(milliseconds: 600));
      
      expect(gameProvider.lastAnswerCorrect, null);
      expect(gameProvider.questionsAttempted, 1);
    });

    test('resetGame clears buffer', () async {
      await gameProvider.fetchQuestion('basic_arithmetic', 'easy');
      gameProvider.resetGame();
      expect(gameProvider.currentQuestion, null);
    });

    test('endGame sets isGameOver to true', () {
      gameProvider.endGame('basic_arithmetic', 'easy', 'TestPlayer', 10.0);
      expect(gameProvider.isGameOver, true);
    });
  });
}
