import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/multiplayer_provider.dart';
import 'game_screen.dart';

class LobbyScreen extends StatefulWidget {
  final String category;
  final String difficulty;
  final String mode;
  final int modeValue;

  const LobbyScreen({
    required this.category,
    required this.difficulty,
    required this.mode,
    required this.modeValue,
    super.key
  });

  @override
  _LobbyScreenState createState() => _LobbyScreenState();
}

class _LobbyScreenState extends State<LobbyScreen> {
  @override
  Widget build(BuildContext context) {
    final mpProvider = context.watch<MultiplayerProvider>();

    print('LobbyScreen Build: gameStarted=${mpProvider.gameStarted}, roomId=${mpProvider.roomId}');

    // Listen for game start signal
    if (mpProvider.gameStarted) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        print('LobbyScreen: Navigating to GameScreen');
        mpProvider.resetMultiplayer(); // Reset the signal
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => GameScreen(
              category: widget.category,
              difficulty: widget.difficulty,
              playerName: mpProvider.playerName ?? 'Player', 
              mode: widget.mode,
              modeValue: widget.modeValue,
              isMultiplayer: true,
            ),
          ),
        );
      });
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Multiplayer Lobby'),
        backgroundColor: Colors.indigo,
        foregroundColor: Colors.white,
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              color: Colors.indigo[50],
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    const Text('Room ID', style: TextStyle(fontSize: 16)),
                    Text(
                      mpProvider.roomId ?? '...',
                      style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Colors.indigo),
                    ),
                    const SizedBox(height: 10),
                    Text('Category: ${widget.category} | Diff: ${widget.difficulty}'),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 30),
            const Text(
              'Current Players:',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            Expanded(
              child: ListView.builder(
                itemCount: mpProvider.playerNames.length,
                itemBuilder: (context, index) {
                  return Card(
                    child: ListTile(
                      leading: const Icon(Icons.person, color: Colors.indigo),
                      title: Text(
                        mpProvider.playerNames[index],
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      trailing: index == 0 
                        ? const Chip(label: Text('Host'), backgroundColor: Colors.amber) 
                        : null,
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: 20),
            if (mpProvider.isHost)
              ElevatedButton(
                onPressed: mpProvider.playerNames.length >= 1 // allow solo test for now
                    ? () => mpProvider.startGame()
                    : null,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: const Text('Start Game for Everyone', style: TextStyle(fontSize: 18)),
              )
            else
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.blue[50],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Center(
                  child: Text(
                    'Waiting for host to start...',
                    style: TextStyle(color: Colors.blue, fontWeight: FontWeight.bold),
                  ),
                ),
              ),
            const SizedBox(height: 10),
            TextButton(
              onPressed: () {
                mpProvider.leaveRoom();
                Navigator.pop(context);
              },
              child: const Text('Leave Lobby', style: TextStyle(color: Colors.red)),
            ),
          ],
        ),
      ),
    );
  }
}
