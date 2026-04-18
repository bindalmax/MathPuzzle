import 'package:mathpuzzle_app/services/api_service.dart';
import 'package:mathpuzzle_app/services/websocket_service.dart';
import 'package:mathpuzzle_app/models/question.dart';
import 'package:mathpuzzle_app/models/highscore.dart';
import 'package:socket_io_client/socket_io_client.dart' as IO;
import 'dart:async';

class MockApiService implements ApiService {
  @override
  String get baseUrl => 'http://localhost';

  @override
  Future<Question> getQuestion(String category, String difficulty) async {
    return Question(
      id: 'test-id',
      text: 'What is 2 + 2?',
      correctAnswer: '4',
      choices: ['2', '3', '4', '5'],
    );
  }

  @override
  Future<List<Highscore>> getLeaderboard({String? category, String? difficulty, int? limit}) async {
    return [
      Highscore(name: 'Alice', score: 100, category: 'basic_arithmetic', difficulty: 'easy', timeTaken: 10.0, questionsAttempted: 10),
    ];
  }

  @override
  Future<void> postScore({
    required String playerName,
    required int score,
    required String category,
    required String difficulty,
    double? timeTaken,
    int? questionsAttempted,
    String? roomId,
  }) async {
    // Do nothing
  }

  @override
  Future<Map<String, dynamic>> createRoom({
    required String playerName,
    required String category,
    required String difficulty,
    String mode = 'time',
    int modeValue = 20,
  }) async {
    return {
      'room_id': 'test-room',
      'players': [playerName],
    };
  }

  @override
  Future<Map<String, dynamic>> joinRoom({
    required String roomId,
    required String playerName,
  }) async {
    return {
      'room_id': roomId,
      'players': ['Host', playerName],
      'category': 'percentage',
      'difficulty': 'medium',
    };
  }

  @override
  Future<List<Map<String, dynamic>>> getAvailableRooms() async {
    return [
      {'room_id': 'room1', 'creator': 'Host1', 'players_count': 1, 'category': 'algebra', 'difficulty': 'medium'}
    ];
  }

  @override
  Future<Map<String, int>> getGameResults(String roomId) async {
    return {'Alice': 10, 'Bob': 8};
  }
}

class MockWebSocketService implements WebSocketService {
  @override
  String get baseUrl => 'http://localhost';

  @override
  IO.Socket? socket;

  @override
  bool get isConnected => true; // Always connected for mock

  final Map<String, List<Function>> _listeners = {};

  MockWebSocketService() {
    socket = MockSocket(this);
  }

  @override
  void connect() {
    // Simulate connection
  }

  @override
  void disconnect() {
    // Simulate disconnect
  }

  @override
  void joinRoom(String roomId, String playerName) {
    // Mock joinRoom
  }

  @override
  void startGame(String roomId, String playerName) {
    // Mock startGame
  }

  @override
  void updateScore(String roomId, String playerName, int score) {
    // Mock updateScore
  }

  // Helper for tests to trigger events
  void triggerEvent(String event, dynamic data) {
    if (_listeners.containsKey(event)) {
      for (var callback in _listeners[event]!) {
        callback(data);
      }
    }
  }
}

// A helper class to mock the IO.Socket behavior for listeners
class MockSocket implements IO.Socket {
  final MockWebSocketService service;
  @override
  bool connected = true;

  MockSocket(this.service);

  @override
  dynamic Function() on(String event, dynamic callback) {
    if (!service._listeners.containsKey(event)) {
      service._listeners[event] = [];
    }
    service._listeners[event]!.add(callback);
    return () {};
  }

  @override
  void emit(String event, [dynamic data]) {
    // No-op for mock
  }

  @override
  IO.Socket connect() => this;
  @override
  IO.Socket disconnect() => this;
  @override
  void dispose() {}
  @override
  IO.Socket close() => this;
  @override
  IO.Socket destroy() => this;
  @override
  String? get id => 'test-id';
  @override
  bool get active => true;
  @override
  bool get disconnected => false;
  
  @override
  void emitWithAck(String event, dynamic data, {Function? ack, bool? binary}) {}
  @override
  IO.Socket open() => this;
  @override
  IO.Socket send(List<dynamic> data) => this;
  
  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}
