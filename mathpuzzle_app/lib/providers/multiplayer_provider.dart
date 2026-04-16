import 'package:flutter/material.dart';
import '../services/websocket_service.dart';
import '../services/api_service.dart';
import '../models/player.dart';

class MultiplayerProvider with ChangeNotifier {
  final WebSocketService webSocketService;
  final ApiService apiService;
  String? _roomId;
  List<Player> _players = [];
  bool _isConnected = false;
  String? _error;

  MultiplayerProvider({required this.webSocketService, required this.apiService}) {
    webSocketService.socket?.on('room_joined', (data) {
      _roomId = data['room_id'];
      _players = (data['players'] as List).map((p) => Player.fromJson(p)).toList();
      _isConnected = true;
      notifyListeners();
    });
  }

  String? get roomId => _roomId;
  List<Player> get players => _players;
  bool get isConnected => _isConnected;
  String? get error => _error;

  Future<void> createRoom(String playerName, String category, String difficulty) async {
    _error = null;
    notifyListeners();
    try {
      final data = await apiService.createRoom(
        playerName: playerName, 
        category: category, 
        difficulty: difficulty
      );
      _roomId = data['room_id'];
      _isConnected = true;
      // After creating room via REST, connect via WebSocket
      webSocketService.joinRoom(_roomId!, playerName);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  void joinRoom(String roomId, String playerName) {
    webSocketService.joinRoom(roomId, playerName);
  }
}
