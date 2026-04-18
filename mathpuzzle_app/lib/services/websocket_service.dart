import 'package:socket_io_client/socket_io_client.dart' as IO;

class WebSocketService {
  IO.Socket? socket;
  final String baseUrl;

  WebSocketService(this.baseUrl);

  bool get isConnected => socket != null && socket!.connected;

  void connect() {
    socket = IO.io(baseUrl, IO.OptionBuilder()
      .setTransports(['websocket'])
      .disableAutoConnect()
      .setExtraHeaders({'origin': 'http://localhost'})
      .build());

    socket?.connect();
    socket?.onConnect((_) => print('WebSocket Connected'));
    socket?.onDisconnect((_) => print('WebSocket Disconnected'));
    socket?.onConnectError((err) => print('WebSocket Connect Error: $err'));
  }

  // Align with backend events in app.py
  void joinRoom(String roomId, String playerName) {
    print('WebSocket: Joining room $roomId as $playerName');
    socket?.emit('join', {'room': roomId, 'name': playerName});
  }

  void startGame(String roomId, String playerName) {
    socket?.emit('start_game_request', {'room': roomId, 'name': playerName});
  }

  void updateScore(String roomId, String playerName, int score) {
    socket?.emit('update_score', {'room': roomId, 'name': playerName, 'score': score});
  }

  void disconnect() {
    socket?.disconnect();
    socket = null;
  }
}
