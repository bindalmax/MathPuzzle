import 'package:flutter/material.dart';
import '../models/question.dart';
import '../services/api_service.dart';

class GameProvider with ChangeNotifier {
  final ApiService apiService;
  Question? _currentQuestion;
  int _score = 0;
  bool _isLoading = false;
  String? _error;
  bool _isGameOver = false;

  GameProvider({required this.apiService});

  Question? get currentQuestion => _currentQuestion;
  int get score => _score;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get isGameOver => _isGameOver;

  Future<void> fetchQuestion(String category, String difficulty) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _currentQuestion = await apiService.getQuestion(category, difficulty);
      _isLoading = false;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
    }
    notifyListeners();
  }

  void submitAnswer(String answer, String category, String difficulty, String playerName) {
    if (_currentQuestion != null && answer == _currentQuestion!.correctAnswer) {
      _score++;
      fetchQuestion(category, difficulty);
    } else {
      _isGameOver = true;
      apiService.postScore(playerName: playerName, score: _score, category: category, difficulty: difficulty);
    }
    notifyListeners();
  }

  void resetGame() {
    _score = 0;
    _isGameOver = false;
    _currentQuestion = null;
    notifyListeners();
  }
}
