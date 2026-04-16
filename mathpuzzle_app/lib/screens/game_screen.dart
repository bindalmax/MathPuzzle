import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:async';
import '../providers/game_provider.dart';

class GameScreen extends StatefulWidget {
  final String category;
  final String difficulty;
  final String playerName;
  final String mode;
  final int modeValue;

  const GameScreen({
    required this.category, 
    required this.difficulty, 
    required this.playerName, 
    this.mode = 'time', 
    this.modeValue = 20, 
    super.key
  });

  @override
  _GameScreenState createState() => _GameScreenState();
}

class _GameScreenState extends State<GameScreen> {
  final TextEditingController _answerController = TextEditingController();
  Timer? _timer;
  late int _timeLeft;
  late int _questionsLeft;
  final Stopwatch _stopwatch = Stopwatch();

  @override
  void initState() {
    super.initState();
    _timeLeft = widget.mode == 'time' ? widget.modeValue : 0;
    _questionsLeft = widget.mode == 'questions' ? widget.modeValue : 0;
    _stopwatch.start();
    
    Future.microtask(() => context.read<GameProvider>().fetchQuestion(widget.category, widget.difficulty));
    
    if (widget.mode == 'time') {
      _startTimer();
    }
  }

  void _startTimer() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_timeLeft > 0) {
        if (mounted) setState(() => _timeLeft--);
      } else {
        _timer?.cancel();
        _onGameEnd();
      }
    });
  }

  void _onGameEnd() {
    if (mounted) {
       _stopwatch.stop();
       final provider = context.read<GameProvider>();
       provider.endGame(
         widget.category, 
         widget.difficulty, 
         widget.playerName, 
         _stopwatch.elapsed.inSeconds.toDouble()
       );
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    _answerController.dispose();
    super.dispose();
  }

  void _submitAnswer(String answer) {
    if (answer.isEmpty) return;
    final provider = context.read<GameProvider>();
    provider.submitAnswer(answer, widget.category, widget.difficulty, widget.playerName);
    _answerController.clear();

    if (widget.mode == 'questions') {
      setState(() {
        if (_questionsLeft > 1) {
          _questionsLeft--;
        } else {
          _questionsLeft = 0;
          _onGameEnd();
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<GameProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Math Puzzle'),
        backgroundColor: Colors.indigo,
        foregroundColor: Colors.white,
      ),
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: BoxDecoration(color: Colors.grey[100]),
        child: provider.isLoading
            ? const Center(child: CircularProgressIndicator())
            : provider.error != null
                ? _buildErrorState(provider)
                : provider.isGameOver
                    ? _buildGameOver(provider)
                    : _buildGameContent(provider),
      ),
    );
  }

  Widget _buildErrorState(GameProvider provider) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, color: Colors.red, size: 60),
            const SizedBox(height: 20),
            Text(provider.error!, textAlign: TextAlign.center, style: const TextStyle(fontSize: 16)),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () => provider.fetchQuestion(widget.category, widget.difficulty),
              child: const Text('Try Again'),
            ),
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Back to Home'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildGameContent(GameProvider provider) {
    if (provider.currentQuestion == null) {
      return const Center(child: Text('Preparing question...'));
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          // Header: Score and Timer/Remaining
          Card(
            elevation: 2,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('Score: ', style: TextStyle(fontSize: 18, color: Colors.grey[600])),
                  Text('${provider.score}', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.green)),
                  const SizedBox(width: 20),
                  const Text('|', style: TextStyle(color: Colors.grey)),
                  const SizedBox(width: 20),
                  if (widget.mode == 'time') ...[
                    Text('Time: ', style: TextStyle(fontSize: 18, color: Colors.grey[600])),
                    Text('${_timeLeft}s', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.orange)),
                  ] else ...[
                    Text('Left: ', style: TextStyle(fontSize: 18, color: Colors.grey[600])),
                    Text('$_questionsLeft', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.blue)),
                  ],
                ],
              ),
            ),
          ),
          const SizedBox(height: 40),

          // Question Box
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 10, offset: const Offset(0, 5))
              ],
            ),
            child: Text(
              provider.currentQuestion?.text ?? '',
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              textAlign: TextAlign.center,
            ),
          ),
          const SizedBox(height: 40),

          // Answer Section
          if (provider.currentQuestion!.choices.isNotEmpty)
            _buildChoices(provider.currentQuestion!.choices)
          else
            _buildTextField(),

          const SizedBox(height: 40),
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('QUIT SESSION', style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }

  Widget _buildChoices(List<String> choices) {
    return Wrap(
      spacing: 15,
      runSpacing: 15,
      alignment: WrapAlignment.center,
      children: choices.map((choice) => SizedBox(
        width: 150,
        height: 60,
        child: ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.white,
            foregroundColor: Colors.indigo,
            side: const BorderSide(color: Colors.indigo, width: 2),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          ),
          onPressed: () => _submitAnswer(choice),
          child: Text(choice, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        ),
      )).toList(),
    );
  }

  Widget _buildTextField() {
    return Column(
      children: [
        TextField(
          controller: _answerController,
          keyboardType: const TextInputType.numberWithOptions(decimal: true, signed: true),
          textAlign: TextAlign.center,
          autofocus: true,
          style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          decoration: InputDecoration(
            hintText: 'Enter solution...',
            enabledBorder: OutlineInputBorder(
              borderSide: const BorderSide(color: Colors.indigo, width: 3),
              borderRadius: BorderRadius.circular(12),
            ),
            focusedBorder: OutlineInputBorder(
              borderSide: const BorderSide(color: Colors.indigo, width: 3),
              borderRadius: BorderRadius.circular(12),
            ),
          ),
          onSubmitted: (val) => _submitAnswer(val),
        ),
        const SizedBox(height: 20),
        SizedBox(
          width: double.infinity,
          height: 60,
          child: ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.indigo, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12))),
            onPressed: () => _submitAnswer(_answerController.text),
            child: const Text('Verify Answer', style: TextStyle(fontSize: 18, color: Colors.white)),
          ),
        ),
      ],
    );
  }

  Widget _buildGameOver(GameProvider provider) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.emoji_events, size: 100, color: Colors.orange),
          const SizedBox(height: 20),
          const Text('Game Over!', style: TextStyle(fontSize: 36, fontWeight: FontWeight.bold, color: Colors.indigo)),
          const SizedBox(height: 10),
          Text('Your Score: ${provider.score}', style: const TextStyle(fontSize: 24)),
          Text('Questions Attempted: ${provider.questionsAttempted}', style: const TextStyle(fontSize: 18, color: Colors.grey)),
          const SizedBox(height: 40),
          ElevatedButton(
            style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 15)),
            onPressed: () {
              provider.resetGame();
              Navigator.pop(context);
            }, 
            child: const Text('Return Home')
          )
        ],
      ),
    );
  }
}
