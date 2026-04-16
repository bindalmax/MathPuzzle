import 'package:flutter/material.dart';
import '../services/websocket_service.dart';
import '../models/player.dart';

class MultiplayerProvider with ChangeNotifier {
  final WebSocketService webSocketService;
  String? _roomId;
  List<Player> _players = [];
  bool _isConnected = false;

  MultiplayerProvider({required this.webSocketService}) {
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

  void createRoom(String playerName, String category, String difficulty) {
    webSocketService.createRoom({'player_name': playerName, 'category': category, 'difficulty': difficulty});
  }

  void joinRoom(String roomId, String playerName) {
    webSocketService.joinRoom(roomId, playerName);
  }
}
