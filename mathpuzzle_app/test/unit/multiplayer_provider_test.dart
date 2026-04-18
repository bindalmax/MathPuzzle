import 'package:flutter_test/flutter_test.dart';
import 'package:mathpuzzle_app/providers/multiplayer_provider.dart';
import '../mocks.dart';

void main() {
  late MultiplayerProvider multiplayerProvider;
  late MockApiService mockApiService;
  late MockWebSocketService mockWebSocketService;

  setUp(() {
    mockApiService = MockApiService();
    mockWebSocketService = MockWebSocketService();
    multiplayerProvider = MultiplayerProvider(
      apiService: mockApiService,
      webSocketService: mockWebSocketService,
    );
  });

  group('MultiplayerProvider Unit Tests', () {
    test('Initial state is correct', () {
      expect(multiplayerProvider.roomId, null);
      expect(multiplayerProvider.playerNames, []);
      expect(multiplayerProvider.gameStarted, false);
    });

    test('createRoom sets roomId and host state', () async {
      await multiplayerProvider.createRoom('HostPlayer', 'algebra', 'medium');
      expect(multiplayerProvider.roomId, 'test-room');
      expect(multiplayerProvider.isHost, true);
    });

    test('joinRoom sets roomId and non-host state via REST and WebSocket', () async {
      await multiplayerProvider.joinRoom('join-room', 'JoinPlayer');
      expect(multiplayerProvider.roomId, 'join-room');
      expect(multiplayerProvider.isHost, false);
      expect(multiplayerProvider.isConnected, true);
    });

    test('Receiving game_start_signal updates gameStarted state', () async {
      await multiplayerProvider.joinRoom('join-room', 'JoinPlayer');
      
      // Simulate receiving WebSocket event
      mockWebSocketService.triggerEvent('game_start_signal', {'room': 'join-room'});
      
      expect(multiplayerProvider.gameStarted, true);
    });

    test('Receiving update_players updates playerNames list', () async {
      await multiplayerProvider.joinRoom('join-room', 'JoinPlayer');
      
      // Simulate receiving WebSocket event
      mockWebSocketService.triggerEvent('update_players', ['Host', 'JoinPlayer']);
      
      expect(multiplayerProvider.playerNames.length, 2);
      expect(multiplayerProvider.playerNames, contains('Host'));
      expect(multiplayerProvider.playerNames, contains('JoinPlayer'));
    });

    test('Receiving score_update updates playerScores map', () async {
      await multiplayerProvider.joinRoom('join-room', 'JoinPlayer');
      
      // Simulate receiving WebSocket event
      mockWebSocketService.triggerEvent('score_update', {
        'players': {'Host': 15, 'JoinPlayer': 12}
      });
      
      expect(multiplayerProvider.playerScores.length, 2);
      expect(multiplayerProvider.playerScores['Host'], 15);
      expect(multiplayerProvider.playerScores['JoinPlayer'], 12);
    });

    test('leaveRoom clears state', () async {
      await multiplayerProvider.createRoom('HostPlayer', 'algebra', 'medium');
      multiplayerProvider.leaveRoom();
      expect(multiplayerProvider.roomId, null);
      expect(multiplayerProvider.playerNames, []);
      expect(multiplayerProvider.isHost, false);
    });

    test('fetchAvailableRooms updates list', () async {
      await multiplayerProvider.fetchAvailableRooms();
      expect(multiplayerProvider.availableRooms.length, 1);
      expect(multiplayerProvider.availableRooms[0]['room_id'], 'room1');
    });

    test('fetchGameResults updates results map', () async {
      await multiplayerProvider.fetchGameResults('test-room');
      expect(multiplayerProvider.multiplayerGameResults, isNotNull);
      expect(multiplayerProvider.multiplayerGameResults!['Alice'], 10);
    });
  });
}
