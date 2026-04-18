import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../models/question.dart';
import '../services/api_service.dart';
import '../services/websocket_service.dart';

class GameProvider with ChangeNotifier {
  final ApiService apiService;
  final WebSocketService? webSocketService;
  
  String? _roomId;
  int? _userId; // Added for User integration
  bool _isMultiplayer = false;

  Question? _currentQuestion;
  Question? _nextQuestion; // Buffer for pre-fetching
  
  int _score = 0;
  int _questionsAttempted = 0;
  bool _isLoading = false;
  String? _error;
  bool _isGameOver = false;

  // Animation/Feedback state
  bool? _lastAnswerCorrect; 

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
  bool? get lastAnswerCorrect => _lastAnswerCorrect;

  void updateMultiplayerInfo({required bool isMultiplayer, String? roomId, int? userId}) {
    _isMultiplayer = isMultiplayer;
    _roomId = roomId;
    _userId = userId;
  }

  // Initial load: Fetch two questions to fill buffer
  Future<void> fetchQuestion(String category, String difficulty) async {
    if (_currentQuestion != null && _nextQuestion != null) return;

    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      if (_currentQuestion == null) {
        _currentQuestion = await apiService.getQuestion(category, difficulty);
      }
      if (_nextQuestion == null) {
        _nextQuestion = await apiService.getQuestion(category, difficulty);
      }
      _isLoading = false;
    } catch (e) {
      _error = "Could not connect to server. Ensure backend is running on port 5005.";
      _isLoading = false;
      print('GameProvider Error: $e');
    }
    notifyListeners();
  }

  // Background fetch to keep buffer full
  Future<void> _prefetchNext(String category, String difficulty) async {
    try {
      _nextQuestion = await apiService.getQuestion(category, difficulty);
      // No notifyListeners here to avoid interrupting gameplay
    } catch (e) {
      print('Prefetch Error: $e');
    }
  }

  void submitAnswer(String answer, String category, String difficulty, String playerName) async {
    if (_currentQuestion == null || _isGameOver || _lastAnswerCorrect != null) return;

    bool isCorrect = false;
    String userAnswer = answer.trim();
    String correctAnswer = _currentQuestion!.correctAnswer.trim();

    print('DEBUG: Submitted: "$userAnswer", Correct: "$correctAnswer"');

    double? userNum = double.tryParse(userAnswer);
    double? correctNum = double.tryParse(correctAnswer);

    if (userNum != null && correctNum != null) {
      isCorrect = (userNum - correctNum).abs() < 0.001;
    } else {
      isCorrect = userAnswer.toLowerCase() == correctAnswer.toLowerCase();
    }

    _lastAnswerCorrect = isCorrect;
    _questionsAttempted++;
    
    if (isCorrect) {
      _score++;
      print('DEBUG: Correct! New Score: $_score');
      HapticFeedback.mediumImpact();
      
      if (_isMultiplayer && webSocketService != null && _roomId != null) {
        webSocketService!.updateScore(_roomId!, playerName, _score);
      }
    } else {
      print('DEBUG: Incorrect!');
      HapticFeedback.heavyImpact();
    }

    notifyListeners();
    
    // DELAY: Wait 500ms to show feedback before switching question
    await Future.delayed(const Duration(milliseconds: 500));

    // TRANSITION: Swap current with next (instant switch)
    if (_nextQuestion != null) {
      _currentQuestion = _nextQuestion;
      _nextQuestion = null;
      _lastAnswerCorrect = null;
      notifyListeners();
      
      // PREFETCH: Get the one after this in background
      _prefetchNext(category, difficulty);
    } else {
      // Fallback if buffer is empty
      _lastAnswerCorrect = null;
      fetchQuestion(category, difficulty);
    }
  }

  void endGame(String category, String difficulty, String playerName, double timeTaken) async {
    if (_isGameOver) return;
    _isGameOver = true;
    HapticFeedback.vibrate();
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
        userId: _userId, // Pass the user ID to link the score
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
    _nextQuestion = null;
    _error = null;
    _lastAnswerCorrect = null;
    notifyListeners();
  }
}
