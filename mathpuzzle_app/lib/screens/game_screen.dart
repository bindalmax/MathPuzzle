import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:async';
import '../providers/game_provider.dart';
import '../providers/multiplayer_provider.dart';

class GameScreen extends StatefulWidget {
  final String category;
  final String difficulty;
  final String playerName;
  final String mode;
  final int modeValue;
  final bool isMultiplayer;

  const GameScreen({
    required this.category, 
    required this.difficulty, 
    required this.playerName, 
    this.mode = 'time', 
    this.modeValue = 20, 
    this.isMultiplayer = false,
    super.key
  });

  @override
  _GameScreenState createState() => _GameScreenState();
}

class _GameScreenState extends State<GameScreen> with SingleTickerProviderStateMixin {
  final TextEditingController _answerController = TextEditingController();
  Timer? _timer;
  late int _timeLeft;
  late int _questionsLeft;
  final Stopwatch _stopwatch = Stopwatch();
  
  late AnimationController _animationController;
  late Animation<double> _shakeAnimation;

  @override
  void initState() {
    super.initState();
    _timeLeft = widget.mode == 'time' ? widget.modeValue : 0;
    _questionsLeft = widget.mode == 'questions' ? widget.modeValue : 0;
    _stopwatch.start();
    
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
    
    _shakeAnimation = TweenSequence<double>([
      TweenSequenceItem(tween: Tween(begin: 0.0, end: 10.0), weight: 1),
      TweenSequenceItem(tween: Tween(begin: 10.0, end: -10.0), weight: 1),
      TweenSequenceItem(tween: Tween(begin: -10.0, end: 10.0), weight: 1),
      TweenSequenceItem(tween: Tween(begin: 10.0, end: 0.0), weight: 1),
    ]).animate(_animationController);

    final gameProvider = context.read<GameProvider>();
    final mpProvider = context.read<MultiplayerProvider>();

    // Synchronize multiplayer state
    gameProvider.updateMultiplayerInfo(
      isMultiplayer: widget.isMultiplayer,
      roomId: mpProvider.roomId,
    );

    Future.microtask(() => gameProvider.fetchQuestion(widget.category, widget.difficulty));
    
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
       
       // If multiplayer, fetch game results after game ends
       if (widget.isMultiplayer && provider.isGameOver) {
         final mpProvider = context.read<MultiplayerProvider>();
         if (mpProvider.roomId != null) {
           mpProvider.fetchGameResults(mpProvider.roomId!);
         }
       }
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    _answerController.dispose();
    _animationController.dispose();
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
    final mpProvider = context.watch<MultiplayerProvider>();

    // Trigger shake if wrong answer
    if (provider.lastAnswerCorrect == false) {
      _animationController.forward(from: 0.0);
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Math Puzzle'),
        backgroundColor: Colors.indigo,
        foregroundColor: Colors.white,
        actions: widget.isMultiplayer 
          ? [
              Builder(
                builder: (context) => IconButton(
                  icon: const Icon(Icons.leaderboard),
                  onPressed: () => Scaffold.of(context).openEndDrawer(),
                ),
              )
            ] 
          : null,
      ),
      endDrawer: widget.isMultiplayer ? _buildLiveScoreboard(mpProvider) : null,
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: BoxDecoration(color: Colors.grey[100]),
        child: provider.isLoading
            ? const Center(child: CircularProgressIndicator())
            : provider.error != null
                ? _buildErrorState(provider)
                : provider.isGameOver
                    ? _buildGameOver(provider, mpProvider)
                    : _buildGameContent(provider),
      ),
    );
  }

  Widget _buildLiveScoreboard(MultiplayerProvider mpProvider) {
    final sortedPlayers = mpProvider.playerScores.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));

    return Drawer(
      child: Column(
        children: [
          const DrawerHeader(
            decoration: BoxDecoration(color: Colors.indigo),
            child: Center(
              child: Text(
                'Live Scores',
                style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
              ),
            ),
          ),
          Expanded(
            child: ListView.builder(
              itemCount: sortedPlayers.length,
              itemBuilder: (context, index) {
                final player = sortedPlayers[index];
                final isMe = player.key == widget.playerName;
                return ListTile(
                  leading: CircleAvatar(
                    backgroundColor: isMe ? Colors.orange : Colors.grey[300],
                    child: Text('${index + 1}'),
                  ),
                  title: Text(
                    player.key + (isMe ? ' (You)' : ''),
                    style: TextStyle(fontWeight: isMe ? FontWeight.bold : FontWeight.normal),
                  ),
                  trailing: Text(
                    '${player.value} pts',
                    style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.indigo),
                  ),
                );
              },
            ),
          ),
        ],
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
          Card(
            elevation: 2,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('Score: ', style: TextStyle(fontSize: 18, color: Colors.grey[600])),
                  AnimatedDefaultTextStyle(
                    duration: const Duration(milliseconds: 300),
                    style: TextStyle(
                      fontSize: 20, 
                      fontWeight: FontWeight.bold, 
                      color: provider.lastAnswerCorrect == true ? Colors.green : Colors.green[800]
                    ),
                    child: Text('${provider.score}'),
                  ),
                  const SizedBox(width: 20),
                  const Text('|', style: TextStyle(color: Colors.grey)),
                  const SizedBox(width: 20),
                  if (widget.mode == 'time') ...[
                    Text('Time: ', style: TextStyle(fontSize: 18, color: Colors.grey[600])),
                    Text('${_timeLeft}s', style: TextStyle(
                      fontSize: 20, 
                      fontWeight: FontWeight.bold, 
                      color: _timeLeft < 10 ? Colors.red : Colors.orange
                    )),
                  ] else ...[
                    Text('Left: ', style: TextStyle(fontSize: 18, color: Colors.grey[600])),
                    Text('$_questionsLeft', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.blue)),
                  ],
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),
          
          if (widget.mode == 'time')
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20.0),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: LinearProgressIndicator(
                  value: _timeLeft / widget.modeValue,
                  minHeight: 10,
                  backgroundColor: Colors.grey[300],
                  valueColor: AlwaysStoppedAnimation<Color>(
                    _timeLeft < 10 ? Colors.red : Colors.indigo
                  ),
                ),
              ),
            ),

          const SizedBox(height: 40),

          AnimatedBuilder(
            animation: _shakeAnimation,
            builder: (context, child) {
              return Transform.translate(
                offset: Offset(_shakeAnimation.value, 0),
                child: child,
              );
            },
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 300),
              width: double.infinity,
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: provider.lastAnswerCorrect == true 
                    ? Colors.green[50] 
                    : provider.lastAnswerCorrect == false 
                        ? Colors.red[50] 
                        : Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: provider.lastAnswerCorrect == true 
                      ? Colors.green 
                      : provider.lastAnswerCorrect == false 
                          ? Colors.red 
                          : Colors.transparent,
                  width: 2
                ),
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
          ),
          const SizedBox(height: 40),

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

  Widget _buildGameOver(GameProvider provider, MultiplayerProvider mpProvider) {
    final scoresToDisplay = (mpProvider.playerScores.isNotEmpty) 
        ? mpProvider.playerScores 
        : mpProvider.multiplayerGameResults;

    List<MapEntry<String, int>> sortedResults = [];
    if (widget.isMultiplayer && scoresToDisplay != null && scoresToDisplay.isNotEmpty) {
      sortedResults = scoresToDisplay.entries.toList()
        ..sort((a, b) => b.value.compareTo(a.value));
    }

    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          TweenAnimationBuilder(
            tween: Tween<double>(begin: 0, end: 1),
            duration: const Duration(seconds: 1),
            builder: (context, double value, child) {
              return Transform.scale(scale: value, child: child);
            },
            child: const Icon(Icons.emoji_events, size: 100, color: Colors.orange),
          ),
          const SizedBox(height: 20),
          const Text('Game Over!', style: TextStyle(fontSize: 36, fontWeight: FontWeight.bold, color: Colors.indigo)),
          const SizedBox(height: 10),
          
          Text('Your Score: ${provider.score}', style: const TextStyle(fontSize: 24)),
          Text('Questions Attempted: ${provider.questionsAttempted}', style: const TextStyle(fontSize: 18, color: Colors.grey)),
          
          if (widget.isMultiplayer) ...[
            const SizedBox(height: 30),
            const Text('Multiplayer Results:', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 10),
            
            if (sortedResults.isNotEmpty)
              ...sortedResults.asMap().entries.map((entry) {
                  int index = entry.key;
                  var playerResult = entry.value;
                  bool isMe = playerResult.key == widget.playerName;
                  return TweenAnimationBuilder(
                    tween: Tween<double>(begin: 0, end: 1),
                    duration: Duration(milliseconds: 300 + (index * 100)),
                    builder: (context, double value, child) {
                      return Opacity(opacity: value, child: child);
                    },
                    child: Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4.0),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text('${index + 1}. ', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                          Text(playerResult.key, style: TextStyle(fontSize: 18, fontWeight: isMe ? FontWeight.bold : FontWeight.normal)),
                          const SizedBox(width: 8),
                          Text('${playerResult.value} pts', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.green)),
                        ],
                      ),
                    ),
                  );
                }).toList()
            else if (mpProvider.error != null)
              Padding(
                padding: const EdgeInsets.all(8.0),
                child: Text('Could not load results: ${mpProvider.error}', style: const TextStyle(color: Colors.red)),
              )
            else
              const Column(
                children: [
                  SizedBox(height: 10),
                  SizedBox(width: 24, height: 24, child: CircularProgressIndicator(strokeWidth: 2)),
                  SizedBox(height: 10),
                  Text('Waiting for other players...', style: TextStyle(fontStyle: FontStyle.italic)),
                ],
              ),
            
            const SizedBox(height: 10),
            const Text('Scores update in real-time', style: TextStyle(fontSize: 12, color: Colors.grey, fontStyle: FontStyle.italic)),
          ],

          const SizedBox(height: 40),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              ElevatedButton.icon(
                icon: const Icon(Icons.refresh),
                label: const Text('Restart Session'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 15),
                ),
                onPressed: () {
                  provider.resetGame();
                  // Re-initialize game with same settings
                  _timeLeft = widget.mode == 'time' ? widget.modeValue : 0;
                  _questionsLeft = widget.mode == 'questions' ? widget.modeValue : 0;
                  _stopwatch.reset();
                  _stopwatch.start();
                  provider.fetchQuestion(widget.category, widget.difficulty);
                  if (widget.mode == 'time') {
                    _startTimer();
                  }
                },
              ),
              const SizedBox(width: 20),
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 15),
                  backgroundColor: Colors.grey[200],
                  foregroundColor: Colors.black87,
                ),
                onPressed: () {
                  provider.resetGame();
                  Navigator.pop(context);
                }, 
                child: const Text('Return Home')
              ),
            ],
          )
        ],
      ),
    );
  }
}
