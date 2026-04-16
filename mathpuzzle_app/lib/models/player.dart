class Player {
  final String id;
  final String name;
  final int score;

  Player({required this.id, required this.name, this.score = 0});

  factory Player.fromJson(Map<String, dynamic> json) {
    return Player(
      id: json['player_id'] ?? '',
      name: json['player_name'] ?? 'Unknown',
      score: json['score'] ?? 0,
    );
  }
}
