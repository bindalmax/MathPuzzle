import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/game_provider.dart';

class GameScreen extends StatefulWidget {
  final String category;
  final String difficulty;
  final String playerName;

  const GameScreen({required this.category, required this.difficulty, required this.playerName, super.key});

  @override
  _GameScreenState createState() => _GameScreenState();
}

class _GameScreenState extends State<GameScreen> {
  final TextEditingController _answerController = TextEditingController();

  @override
  void initState() {
    super.initState();
    Future.microtask(() => context.read<GameProvider>().fetchQuestion(widget.category, widget.difficulty));
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<GameProvider>();

    return Scaffold(
      appBar: AppBar(title: Text('Score: ${provider.score}')),
      body: provider.isLoading
          ? const Center(child: CircularProgressIndicator())
          : provider.isGameOver
              ? Center(child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Text('Game Over!', style: TextStyle(fontSize: 32)),
                    ElevatedButton(onPressed: () {
                      provider.resetGame();
                      Navigator.pop(context);
                    }, child: const Text('Home'))
                  ],
                ))
              : Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      Text(provider.currentQuestion?.text ?? '', style: const TextStyle(fontSize: 24)),
                      TextField(controller: _answerController, keyboardType: TextInputType.number),
                      ElevatedButton(onPressed: () {
                        provider.submitAnswer(_answerController.text, widget.category, widget.difficulty, widget.playerName);
                        _answerController.clear();
                      }, child: const Text('Submit')),
                    ],
                  ),
                ),
    );
  }
}
