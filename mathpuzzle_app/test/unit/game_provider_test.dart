import 'package:flutter_test/flutter_test.dart';
import 'package:mathpuzzle_app/providers/game_provider.dart';
import '../mocks.dart';

void main() {
  late GameProvider gameProvider;
  late MockApiService mockApiService;

  setUp(() {
    mockApiService = MockApiService();
    gameProvider = GameProvider(apiService: mockApiService);
  });

  group('GameProvider Unit Tests', () {
    test('Initial state is correct', () {
      expect(gameProvider.score, 0);
      expect(gameProvider.questionsAttempted, 0);
      expect(gameProvider.isGameOver, false);
      expect(gameProvider.currentQuestion, null);
    });

    test('fetchQuestion updates currentQuestion', () async {
      await gameProvider.fetchQuestion('basic_arithmetic', 'easy');
      expect(gameProvider.currentQuestion, isNotNull);
      expect(gameProvider.currentQuestion!.text, 'What is 2 + 2?');
      expect(gameProvider.isLoading, false);
    });

    test('submitAnswer increments score on correct answer', () async {
      await gameProvider.fetchQuestion('basic_arithmetic', 'easy');
      gameProvider.submitAnswer('4', 'basic_arithmetic', 'easy', 'TestPlayer');
      expect(gameProvider.score, 1);
      expect(gameProvider.questionsAttempted, 1);
    });

    test('submitAnswer increments attempted but not score on wrong answer', () async {
      await gameProvider.fetchQuestion('basic_arithmetic', 'easy');
      gameProvider.submitAnswer('5', 'basic_arithmetic', 'easy', 'TestPlayer');
      expect(gameProvider.score, 0);
      expect(gameProvider.questionsAttempted, 1);
    });

    test('resetGame clears state', () async {
      await gameProvider.fetchQuestion('basic_arithmetic', 'easy');
      gameProvider.submitAnswer('4', 'basic_arithmetic', 'easy', 'TestPlayer');
      gameProvider.resetGame();
      expect(gameProvider.score, 0);
      expect(gameProvider.questionsAttempted, 0);
      expect(gameProvider.currentQuestion, null);
    });

    test('endGame sets isGameOver to true', () {
      gameProvider.endGame('basic_arithmetic', 'easy', 'TestPlayer', 10.0);
      expect(gameProvider.isGameOver, true);
    });
  });
}
