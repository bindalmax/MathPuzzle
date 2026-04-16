import 'package:flutter/material.dart';
import '../models/question.dart';
import '../services/api_service.dart';

class GameProvider with ChangeNotifier {
  final ApiService apiService;
  Question? _currentQuestion;
  int _score = 0;
  int _questionsAttempted = 0;
  bool _isLoading = false;
  String? _error;
  bool _isGameOver = false;

  GameProvider({required this.apiService});

  Question? get currentQuestion => _currentQuestion;
  int get score => _score;
  int get questionsAttempted => _questionsAttempted;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get isGameOver => _isGameOver;

  Future<void> fetchQuestion(String category, String difficulty) async {
    _isLoading = true;
    _error = null;
    _currentQuestion = null;
    notifyListeners();

    try {
      _currentQuestion = await apiService.getQuestion(category, difficulty);
      _isLoading = false;
    } catch (e) {
      _error = "Could not connect to server. Ensure backend is running on port 5005.";
      _isLoading = false;
      print('GameProvider Error: $e');
    }
    notifyListeners();
  }

  void submitAnswer(String answer, String category, String difficulty, String playerName) async {
    if (_currentQuestion == null || _isGameOver) return;

    bool isCorrect = false;
    String userAnswer = answer.trim();
    String correctAnswer = _currentQuestion!.correctAnswer.trim();

    print('DEBUG: Submitted: "$userAnswer", Correct: "$correctAnswer"');

    // Try numeric comparison first
    double? userNum = double.tryParse(userAnswer);
    double? correctNum = double.tryParse(correctAnswer);

    if (userNum != null && correctNum != null) {
      isCorrect = (userNum - correctNum).abs() < 0.001;
    } else {
      isCorrect = userAnswer.toLowerCase() == correctAnswer.toLowerCase();
    }

    _questionsAttempted++;
    if (isCorrect) {
      _score++;
      print('DEBUG: Correct! New Score: $_score');
    } else {
      print('DEBUG: Incorrect!');
    }
    
    // Notify listeners so the score updates in UI before/during next fetch
    notifyListeners();

    // Always fetch a new question to keep the game moving (like web)
    fetchQuestion(category, difficulty);
  }

  // Explicitly end the game (called by Timer or Question Limit in UI)
  void endGame(String category, String difficulty, String playerName, double timeTaken) async {
    if (_isGameOver) return;
    _isGameOver = true;
    notifyListeners();

    try {
      await apiService.postScore(
        playerName: playerName,
        score: _score,
        category: category,
        difficulty: difficulty,
        timeTaken: timeTaken,
        questionsAttempted: _questionsAttempted,
      );
    } catch (e) {
      print('Failed to save score: $e');
    }
  }

  void resetGame() {
    _score = 0;
    _questionsAttempted = 0;
    _isGameOver = false;
    _currentQuestion = null;
    _error = null;
    notifyListeners();
  }
}
