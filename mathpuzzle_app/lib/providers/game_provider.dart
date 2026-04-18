import 'package:flutter/material.dart';
import '../models/question.dart';
import '../services/api_service.dart';
import '../services/websocket_service.dart';

class GameProvider with ChangeNotifier {
  final ApiService apiService;
  final WebSocketService? webSocketService;
  
  String? _roomId;
  bool _isMultiplayer = false;

  Question? _currentQuestion;
  int _score = 0;
  int _questionsAttempted = 0;
  bool _isLoading = false;
  String? _error;
  bool _isGameOver = false;

  GameProvider({
    required this.apiService,
    this.webSocketService,
  });

  Question? get currentQuestion => _currentQuestion;
  int get score => _score;
  int get questionsAttempted => _questionsAttempted;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get isGameOver => _isGameOver;
  bool get isMultiplayer => _isMultiplayer;

  void updateMultiplayerInfo({required bool isMultiplayer, String? roomId}) {
    _isMultiplayer = isMultiplayer;
    _roomId = roomId;
    // Don't notifyListeners here to avoid unnecessary builds during screen transitions
  }

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
      
      // Emit score update for multiplayer
      if (_isMultiplayer && webSocketService != null && _roomId != null) {
        webSocketService!.updateScore(_roomId!, playerName, _score);
      }
    } else {
      print('DEBUG: Incorrect!');
    }

    notifyListeners();
    fetchQuestion(category, difficulty);
  }

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
        roomId: _roomId,
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
