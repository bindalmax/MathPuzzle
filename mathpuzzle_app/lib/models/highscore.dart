class Highscore {
  final String name;
  final int score;
  final String category;
  final String difficulty;
  final double? timeTaken;
  final int? questionsAttempted;

  Highscore({
    required this.name,
    required this.score,
    required this.category,
    required this.difficulty,
    this.timeTaken,
    this.questionsAttempted,
  });

  factory Highscore.fromJson(Map<String, dynamic> json) {
    return Highscore(
      name: json['name'] ?? 'Unknown',
      score: json['score'] ?? 0,
      category: json['category'] ?? '',
      difficulty: json['difficulty'] ?? '',
      timeTaken: json['time_taken']?.toDouble(),
      questionsAttempted: json['questions_attempted'],
    );
  }
}
