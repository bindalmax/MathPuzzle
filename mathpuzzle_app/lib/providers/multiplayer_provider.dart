import 'package:flutter/material.dart';
import '../services/websocket_service.dart';
import '../services/api_service.dart';
import '../models/player.dart';

class MultiplayerProvider with ChangeNotifier {
  final WebSocketService webSocketService;
  final ApiService apiService;
  
  String? _roomId;
  List<String> _playerNames = [];
  Map<String, int> _playerScores = {};
  bool _isConnected = false;
  bool _gameStarted = false;
  String? _error;
  String? _playerName;
  bool _isHost = false;
  bool _isJoining = false;

  // New state variables for room discovery and game results
  List<Map<String, dynamic>> _availableRooms = [];
  Map<String, int>? _multiplayerGameResults;

  List<Map<String, dynamic>> get availableRooms => _availableRooms;
  Map<String, int>? get multiplayerGameResults => _multiplayerGameResults;
  bool get isJoining => _isJoining;

  // Method to fetch available rooms
  Future<void> fetchAvailableRooms() async {
    try {
      _availableRooms = await apiService.getAvailableRooms();
      notifyListeners();
    } catch (e) {
      _error = 'Failed to load rooms: $e';
      notifyListeners();
    }
  }

  // Method to fetch multiplayer game results
  Future<void> fetchGameResults(String roomId) async {
    try {
      _multiplayerGameResults = await apiService.getGameResults(roomId);
      notifyListeners();
    } catch (e) {
      _error = 'Failed to load game results: $e';
      notifyListeners();
    }
  }
  
  MultiplayerProvider({required this.webSocketService, required this.apiService}) {
    _isConnected = webSocketService.isConnected;
    _setupListeners();
  }

  void _setupListeners() {
    webSocketService.socket?.on('update_players', (data) {
      print('MultiplayerProvider: Received update_players: $data');
      _playerNames = List<String>.from(data);
      notifyListeners();
    });

    webSocketService.socket?.on('game_start_signal', (data) {
      print('MultiplayerProvider: Received game_start_signal: $data');
      _gameStarted = true;
      _multiplayerGameResults = null; 
      notifyListeners();
    });

    webSocketService.socket?.on('score_update', (data) {
      print('MultiplayerProvider: Received score_update: $data');
      if (data != null && data['players'] != null) {
        _playerScores = Map<String, int>.from(
          (data['players'] as Map).map((key, value) => MapEntry(key.toString(), value as int))
        );
        notifyListeners();
      }
    });

    webSocketService.socket?.on('connect', (_) {
      print('MultiplayerProvider: Socket Connected');
      _isConnected = true;
      if (_roomId != null && _playerName != null && !_isJoining) {
        print('MultiplayerProvider: Re-joining room $_roomId');
        webSocketService.joinRoom(_roomId!, _playerName!);
      }
      notifyListeners();
    });

    webSocketService.socket?.on('disconnect', (_) {
      print('MultiplayerProvider: Socket Disconnected');
      _isConnected = false;
      notifyListeners();
    });
  }

  String? get roomId => _roomId;
  String? get playerName => _playerName;
  List<String> get playerNames => _playerNames;
  Map<String, int> get playerScores => _playerScores;
  bool get isConnected => _isConnected;
  bool get gameStarted => _gameStarted;
  bool get isHost => _isHost;
  String? get error => _error;

  Future<void> createRoom(String playerName, String category, String difficulty) async {
    _error = null;
    _isJoining = true;
    _playerName = playerName;
    _isHost = true;
    _playerScores = {};
    _playerNames = [];
    _gameStarted = false;
    _multiplayerGameResults = null;
    notifyListeners();
    
    try {
      if (!webSocketService.isConnected) {
        webSocketService.connect();
      }

      final data = await apiService.createRoom(
        playerName: playerName, 
        category: category, 
        difficulty: difficulty
      );
      
      _roomId = data['room_id'];
      _isConnected = true;
      webSocketService.joinRoom(_roomId!, playerName);
      await fetchAvailableRooms(); 
    } catch (e) {
      _error = e.toString();
      _isHost = false;
      _roomId = null;
    } finally {
      _isJoining = false;
      notifyListeners();
    }
  }

  Future<void> joinRoom(String roomId, String playerName) async {
    _error = null;
    _isJoining = true;
    _playerName = playerName;
    _isHost = false;
    _playerScores = {};
    _playerNames = [];
    _gameStarted = false;
    _multiplayerGameResults = null;
    notifyListeners();

    try {
      if (!webSocketService.isConnected) {
        webSocketService.connect();
      }

      final data = await apiService.joinRoom(roomId: roomId, playerName: playerName);
      
      _roomId = data['room_id'];
      _isConnected = true;
      webSocketService.joinRoom(_roomId!, playerName);
    } catch (e) {
      _error = e.toString();
      _roomId = null;
    } finally {
      _isJoining = false;
      notifyListeners();
    }
  }

  void startGame() {
    if (_isHost && _roomId != null && _playerName != null) {
      print('MultiplayerProvider: Requesting game start for room $_roomId');
      webSocketService.startGame(_roomId!, _playerName!);
    }
  }

  void resetMultiplayer() {
    _gameStarted = false;
    notifyListeners();
  }

  void leaveRoom() {
    print('MultiplayerProvider: Leaving room $_roomId');
    _roomId = null;
    _playerName = null;
    _playerNames = [];
    _playerScores = {};
    _isConnected = false;
    _gameStarted = false;
    _isHost = false;
    _availableRooms = []; 
    _multiplayerGameResults = null;
    webSocketService.disconnect();
    webSocketService.connect(); 
    notifyListeners();
  }
}
