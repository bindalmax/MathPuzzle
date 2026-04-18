import 'package:mathpuzzle_app/services/api_service.dart';
import 'package:mathpuzzle_app/services/websocket_service.dart';
import 'package:mathpuzzle_app/models/question.dart';
import 'package:mathpuzzle_app/models/highscore.dart';
import 'package:socket_io_client/socket_io_client.dart' as IO;
import 'package:google_sign_in/google_sign_in.dart';
import 'dart:async';

class MockGoogleSignInAccount implements GoogleSignInAccount {
  @override
  String get displayName => 'Mock User';
  @override
  String get email => 'mock@example.com';
  @override
  String get id => 'mock-id-123';
  @override
  String? get photoUrl => null;
  @override
  String? get serverAuthCode => null;

  @override
  GoogleSignInAuthentication get authentication => MockGoogleSignInAuthentication();

  @override
  Future<Map<String, String>> get authHeaders async => {};

  @override
  Future<void> clearAuthCache() async {}

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class MockGoogleSignInAuthentication implements GoogleSignInAuthentication {
  @override
  String? get accessToken => 'mock-access-token';
  @override
  String? get idToken => 'mock-id-token';

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class MockGoogleSignIn implements GoogleSignIn {
  bool shouldReturnUser = true;

  @override
  Future<GoogleSignInAccount?> signIn() async {
    return shouldReturnUser ? MockGoogleSignInAccount() : null;
  }

  @override
  Future<GoogleSignInAccount?> signOut() async => null;
  @override
  Future<GoogleSignInAccount?> disconnect() async => null;
  @override
  Future<bool> isSignedIn() async => false;
  @override
  Future<GoogleSignInAccount?> signInSilently({bool suppressErrors = true, bool reAuthenticate = false}) async => null;
  
  @override
  Stream<GoogleSignInAccount?> get onCurrentUserChanged => Stream.value(null);
  
  @override
  GoogleSignInAccount? get currentUser => null;

  @override
  List<String> get scopes => [];

  @override
  String? get hostedDomain => null;

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

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
      Highscore(name: 'Alice', score: 100, category: 'basic_arithmetic', difficulty: 'easy', timeTaken: 10.0),
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
    int? userId,
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

  @override
  Future<Map<String, dynamic>> authenticateGoogle(String idToken) async {
    return {
      'user_id': 1,
      'display_name': 'Mock User',
      'email': 'mock@example.com',
    };
  }
}

class MockWebSocketService implements WebSocketService {
  @override
  String get baseUrl => 'http://localhost';

  @override
  IO.Socket? socket;

  @override
  bool get isConnected => true; 

  final Map<String, List<Function>> _listeners = {};

  MockWebSocketService() {
    socket = MockSocket(this);
  }

  @override
  void connect() {
  }

  @override
  void disconnect() {
  }

  @override
  void joinRoom(String roomId, String playerName) {
  }

  @override
  void startGame(String roomId, String playerName) {
  }

  @override
  void updateScore(String roomId, String playerName, int score) {
  }

  void triggerEvent(String event, dynamic data) {
    if (_listeners.containsKey(event)) {
      for (var callback in _listeners[event]!) {
        callback(data);
      }
    }
  }
}

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
