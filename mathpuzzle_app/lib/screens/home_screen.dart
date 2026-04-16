import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../models/highscore.dart';
import '../widgets/leaderboard_widget.dart';
import '../providers/multiplayer_provider.dart';
import 'game_screen.dart';

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
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Creating Multiplayer Lobby...')));
      // Navigation to Lobby would happen based on Provider state change (future improvement)
    }
  }

  @override
  Widget build(BuildContext context) {
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
                      
                      // Game Type
                      const Text('Game Type:', style: TextStyle(fontWeight: FontWeight.bold)),
                      Row(
                        children: [
                          Expanded(
                            child: RadioListTile<String>(
                              title: const Text('Single'),
                              value: 'single',
                              groupValue: _gameType,
                              onChanged: (val) => setState(() => _gameType = val!),
                            ),
                          ),
                          Expanded(
                            child: RadioListTile<String>(
                              title: const Text('Multi'),
                              value: 'multiplayer',
                              groupValue: _gameType,
                              onChanged: (val) => setState(() => _gameType = val!),
                            ),
                          ),
                        ],
                      ),
                      const Divider(),

                      // Category
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

                      // Difficulty
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

                      // Mode
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

                      // Mode Value
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
                        onPressed: _onStartButtonPressed,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.indigo,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                        ),
                        child: Text(_gameType == 'multiplayer' ? 'Create Multiplayer Lobby' : 'Start Single Player Game'),
                      ),
                    ],
                  ),
                ),
              ),
              
              const SizedBox(height: 20),
              
              // Join Lobby Card (Mockup)
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
                      // Since we don't have real-time room list in API yet, show a placeholder
                      const Text('No active lobbies found.', style: TextStyle(color: Colors.grey)),
                      const SizedBox(height: 10),
                      TextField(
                        decoration: const InputDecoration(
                          labelText: 'Enter Room ID manually:',
                          border: OutlineInputBorder(),
                        ),
                        onSubmitted: (val) {
                           if (val.isNotEmpty) {
                              context.read<MultiplayerProvider>().joinRoom(val, _nameController.text);
                           }
                        },
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
}
