import 'package:socket_io_client/socket_io_client.dart' as IO;

class WebSocketService {
  IO.Socket? socket;
  final String baseUrl;

  WebSocketService(this.baseUrl);

  void connect() {
    socket = IO.io(baseUrl, IO.OptionBuilder()
      .setTransports(['websocket'])
      .disableAutoConnect()
      .build());

    socket?.connect();
    socket?.onConnect((_) => print('WebSocket Connected'));
    socket?.onDisconnect((_) => print('WebSocket Disconnected'));
  }

  void createRoom(Map<String, dynamic> data) => socket?.emit('create_room', data);
  void joinRoom(String roomId, String playerName) => socket?.emit('join_room', {'room_id': roomId, 'player_name': playerName});
  void disconnect() => socket?.disconnect();
}
