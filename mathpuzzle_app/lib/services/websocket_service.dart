import 'package:socket_io_client/socket_io_client.dart' as IO;

class WebSocketService {
  IO.Socket? socket;
  final String baseUrl;

  WebSocketService(this.baseUrl);

  void connect() {
    socket = IO.io(baseUrl, IO.OptionBuilder()
      .setTransports(['websocket'])
      .disableAutoConnect()
      // Bypass SSL verification for local development (WSS)
      .setExtraHeaders({'origin': 'http://localhost'}) // Sometimes helps with CORS
      .setQuery({'token': 'dev'}) 
      .enableForceNew()
      .build());
    
    // Note: socket_io_client doesn't have a direct 'badCertificateCallback'
    // but relies on the underlying HttpClient. Since we set HttpOverrides.global
    // in main.dart, it should ideally use it. However, forcing websocket 
    // transport often bypasses some of the handshakes that cause cert issues.

    socket?.connect();
    socket?.onConnect((_) => print('WebSocket Connected'));
    socket?.onDisconnect((_) => print('WebSocket Disconnected'));
    socket?.onConnectError((err) => print('WebSocket Connect Error: $err'));
  }

  void createRoom(Map<String, dynamic> data) => socket?.emit('create_room', data);
  void joinRoom(String roomId, String playerName) => socket?.emit('join_room', {'room_id': roomId, 'player_name': playerName});
  void disconnect() => socket?.disconnect();
}
