import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../models/highscore.dart';
import '../widgets/leaderboard_widget.dart';
import 'game_screen.dart';

class HomeScreen extends StatefulWidget {
  final ApiService apiService;
  final String baseUrl;

  const HomeScreen({required this.apiService, required this.baseUrl, super.key});

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String _playerName = 'Player';
  String _selectedCategory = 'basic_arithmetic';
  String _selectedDifficulty = 'easy';
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Math Puzzle')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              decoration: const InputDecoration(labelText: 'Name'),
              onChanged: (value) => _playerName = value,
            ),
            DropdownButton<String>(
              value: _selectedCategory,
              items: ['basic_arithmetic', 'decimal_fraction', 'percentage'].map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
              onChanged: (value) => setState(() => _selectedCategory = value!),
            ),
            DropdownButton<String>(
              value: _selectedDifficulty,
              items: ['easy', 'medium', 'hard'].map((d) => DropdownMenuItem(value: d, child: Text(d))).toList(),
              onChanged: (value) => setState(() => _selectedDifficulty = value!),
            ),
            ElevatedButton(
              onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => GameScreen(category: _selectedCategory, difficulty: _selectedDifficulty, playerName: _playerName))),
              child: const Text('Start Game'),
            ),
            const SizedBox(height: 20),
            const Text('Leaderboard', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            LeaderboardWidget(scores: _leaderboard.map((s) => {'name': s.name, 'score': s.score, 'category': s.category}).toList()),
          ],
        ),
      ),
    );
  }
}
