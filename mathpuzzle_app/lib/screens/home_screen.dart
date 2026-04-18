import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../models/highscore.dart';
import '../widgets/leaderboard_widget.dart';
import '../providers/multiplayer_provider.dart';
import 'game_screen.dart';
import 'lobby_screen.dart'; // Import LobbyScreen

class HomeScreen extends StatefulWidget {
  final ApiService apiService;
  final String baseUrl;

  const HomeScreen({required this.apiService, required this.baseUrl, super.key});

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _nameController = TextEditingController(text: 'MathWizard');
  String _selectedCategory = 'basic_arithmetic';
  String _selectedDifficulty = 'medium';
  String _gameType = 'single'; // 'single' or 'multiplayer'
  String _gameMode = 'time'; // 'time' or 'questions'
  int _modeValue = 20;

  List<Highscore> _leaderboard = [];

  @override
  void initState() {
    super.initState();
    _loadLeaderboard();
    
    // Setup listener for navigation
    final mpProvider = context.read<MultiplayerProvider>();
    mpProvider.addListener(_handleMultiplayerStateChange);
    
    // Fetch available rooms
    Future.microtask(() => mpProvider.fetchAvailableRooms());
  }

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  void _handleMultiplayerStateChange() {
    if (!mounted) return;
    
    final mpProvider = context.read<MultiplayerProvider>();
    
    // Navigate to lobby if roomId is set and we are not currently joining
    if (mpProvider.roomId != null && mpProvider.isConnected && !mpProvider.isJoining) {
      // Check if we are already showing the LobbyScreen to avoid duplicate pushes
      // In a real app, you might use a more robust routing solution
      _navigateToLobby(mpProvider);
    }
  }

  bool _isNavigatingToLobby = false;

  void _navigateToLobby(MultiplayerProvider mpProvider) async {
    if (_isNavigatingToLobby) return;
    _isNavigatingToLobby = true;

    // Find the room details if it was joined from the list
    final roomDetails = mpProvider.availableRooms.firstWhere(
      (r) => r['room_id'] == mpProvider.roomId,
      orElse: () => {
        'category': _selectedCategory,
        'difficulty': _selectedDifficulty,
        'mode': _gameMode,
        'mode_value': _modeValue,
      },
    );

    print('HomeScreen: Navigating to Lobby ${mpProvider.roomId}');

    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => LobbyScreen(
          category: roomDetails['category'] ?? _selectedCategory,
          difficulty: roomDetails['difficulty'] ?? _selectedDifficulty,
          mode: roomDetails['mode'] ?? _gameMode,
          modeValue: roomDetails['mode_value'] ?? _modeValue,
        ),
      ),
    );

    // Cleanup on return
    _isNavigatingToLobby = false;
    if (mpProvider.roomId != null) {
      mpProvider.leaveRoom(); 
    }
  }

  void _loadLeaderboard() async {
    try {
      final scores = await widget.apiService.getLeaderboard(limit: 5);
      setState(() => _leaderboard = scores);
    } catch (e) {
      print('Error loading leaderboard: $e');
    }
  }

  void _onStartButtonPressed() {
    String playerName = _nameController.text.trim();
    if (playerName.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter a GamerId')));
      return;
    }

    if (_gameType == 'single') {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => GameScreen(
            category: _selectedCategory,
            difficulty: _selectedDifficulty,
            playerName: playerName,
            mode: _gameMode,
            modeValue: _modeValue,
          ),
        ),
      ).then((_) => _loadLeaderboard()); // Reload when coming back
    } else {
      // Multiplayer logic
      context.read<MultiplayerProvider>().createRoom(playerName, _selectedCategory, _selectedDifficulty);
    }
  }

  @override
  Widget build(BuildContext context) {
    final mpProvider = context.watch<MultiplayerProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Math Puzzle'),
        backgroundColor: Colors.indigo,
        foregroundColor: Colors.white,
      ),
      body: Container(
        decoration: BoxDecoration(color: Colors.grey[100]),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                'Welcome to the Math Game!',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.indigo),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              
              // Setup Game Card
              Card(
                elevation: 4,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Start New Game', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 15),
                      TextField(
                        controller: _nameController,
                        decoration: const InputDecoration(
                          labelText: 'Enter your GamerId:',
                          border: OutlineInputBorder(),
                          hintText: 'e.g. MathWizard',
                        ),
                      ),
                      const SizedBox(height: 20),
                      
                      // Game Type Selector
                      const Text('Game Type:', style: TextStyle(fontWeight: FontWeight.bold)),
                      Row(
                        children: [
                          Expanded(
                            child: RadioListTile<String>(
                              title: const Text('Single'),
                              value: 'single',
                              groupValue: _gameType,
                              onChanged: (val) {
                                setState(() => _gameType = val!);
                              },
                            ),
                          ),
                          Expanded(
                            child: RadioListTile<String>(
                              title: const Text('Multi'),
                              value: 'multiplayer',
                              groupValue: _gameType,
                              onChanged: (val) {
                                setState(() => _gameType = val!);
                                // Pre-connect WebSocket if selecting multi
                                if (!mpProvider.isConnected) {
                                  mpProvider.webSocketService.connect(); 
                                }
                              },
                            ),
                          ),
                        ],
                      ),
                      const Divider(),

                      // Category Selector
                      const Text('Category:'),
                      DropdownButton<String>(
                        isExpanded: true,
                        value: _selectedCategory,
                        items: const [
                          DropdownMenuItem(value: 'basic_arithmetic', child: Text('Basic Arithmetic')),
                          DropdownMenuItem(value: 'decimal_fraction', child: Text('Decimals & Fractions')),
                          DropdownMenuItem(value: 'percentage', child: Text('Percentages')),
                          DropdownMenuItem(value: 'profit_loss', child: Text('Profit & Loss')),
                          DropdownMenuItem(value: 'algebra', child: Text('Algebra')),
                        ],
                        onChanged: (value) => setState(() => _selectedCategory = value!),
                      ),
                      const SizedBox(height: 15),

                      // Difficulty Selector
                      const Text('Difficulty:'),
                      DropdownButton<String>(
                        isExpanded: true,
                        value: _selectedDifficulty,
                        items: const [
                          DropdownMenuItem(value: 'easy', child: Text('Easy')),
                          DropdownMenuItem(value: 'medium', child: Text('Medium')),
                          DropdownMenuItem(value: 'hard', child: Text('Hard')),
                        ],
                        onChanged: (value) => setState(() => _selectedDifficulty = value!),
                      ),
                      const SizedBox(height: 15),

                      // Game Mode Selector
                      const Text('Game Mode:'),
                      DropdownButton<String>(
                        isExpanded: true,
                        value: _gameMode,
                        items: const [
                          DropdownMenuItem(value: 'time', child: Text('Time Mode')),
                          DropdownMenuItem(value: 'questions', child: Text('Question Count Mode')),
                        ],
                        onChanged: (value) => setState(() => _gameMode = value!),
                      ),
                      const SizedBox(height: 15),

                      // Mode Value Slider
                      Text(_gameMode == 'time' ? 'Time in seconds (5-300):' : 'Number of questions (1-100):'),
                      Slider(
                        value: _modeValue.toDouble(),
                        min: _gameMode == 'time' ? 5 : 1,
                        max: _gameMode == 'time' ? 300 : 100,
                        divisions: _gameMode == 'time' ? 59 : 99,
                        label: _modeValue.toString(),
                        onChanged: (val) => setState(() => _modeValue = val.toInt()),
                      ),
                      Center(child: Text('Value: $_modeValue', style: const TextStyle(fontWeight: FontWeight.bold))),
                      
                      const SizedBox(height: 20),
                      ElevatedButton(
                        onPressed: mpProvider.isJoining ? null : _onStartButtonPressed,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.indigo,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                        ),
                        child: mpProvider.isJoining 
                          ? const CircularProgressIndicator(color: Colors.white)
                          : Text(_gameType == 'multiplayer' ? 'Create Multiplayer Lobby' : 'Start Single Player Game'),
                      ),
                    ],
                  ),
                ),
              ),
              
              const SizedBox(height: 20),
              
              // Join Lobby Card
              Card(
                elevation: 4,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Join Active Lobby', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 10),
                      
                      if (mpProvider.error != null)
                        Padding(
                          padding: const EdgeInsets.only(bottom: 10.0),
                          child: Text(mpProvider.error!, style: const TextStyle(color: Colors.red)),
                        ),

                      // Display available rooms
                      if (mpProvider.availableRooms.isNotEmpty)
                        ...mpProvider.availableRooms.map((room) => _buildRoomListItem(room, mpProvider)).toList()
                      else if (mpProvider.error == null && !mpProvider.isJoining)
                        const Text('No active lobbies found.', style: TextStyle(color: Colors.grey)),
                      
                      if (mpProvider.isJoining)
                        const Center(child: Padding(
                          padding: EdgeInsets.symmetric(vertical: 20.0),
                          child: CircularProgressIndicator(),
                        )),

                      const SizedBox(height: 10),
                      TextField(
                        decoration: const InputDecoration(
                          labelText: 'Enter Room ID manually:',
                          border: OutlineInputBorder(),
                        ),
                        onSubmitted: (val) {
                           if (val.isNotEmpty && !mpProvider.isJoining) {
                              mpProvider.joinRoom(val, _nameController.text.trim());
                           }
                        },
                      ),
                      const SizedBox(height: 10),
                      OutlinedButton.icon(
                        icon: const Icon(Icons.refresh),
                        label: const Text('Refresh Rooms'),
                        onPressed: mpProvider.isJoining ? null : mpProvider.fetchAvailableRooms,
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 30),
              const Text('Global Hall of Fame', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.indigo)),
              const SizedBox(height: 10),
              _leaderboard.isEmpty 
                ? const Text('Loading leaderboard...') 
                : LeaderboardWidget(scores: _leaderboard.map((s) => {'name': s.name, 'score': s.score, 'category': s.category}).toList()),
              
              const SizedBox(height: 40),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRoomListItem(Map<String, dynamic> room, MultiplayerProvider mpProvider) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 6.0),
      child: ListTile(
        title: Text('Room: ${room['room_id']}'),
        subtitle: Text('Creator: ${room['creator']} | ${room['players_count']} players | ${room['category']} (${room['difficulty']})'),
        trailing: ElevatedButton(
          onPressed: mpProvider.isJoining ? null : () => mpProvider.joinRoom(room['room_id'], _nameController.text.trim()),
          child: const Text('Join'),
        ),
        onTap: mpProvider.isJoining ? null : () => mpProvider.joinRoom(room['room_id'], _nameController.text.trim()),
      ),
    );
  }
}
