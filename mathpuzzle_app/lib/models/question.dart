class Question {
  final String id;
  final String text;
  final List<String> choices;
  final String correctAnswer;

  Question({required this.id, required this.text, this.choices = const [], required this.correctAnswer});

  factory Question.fromJson(Map<String, dynamic> json) {
    return Question(
      id: json['question_id'] ?? '',
      text: json['question'] ?? '',
      choices: List<String>.from(json['choices'] ?? []),
      correctAnswer: json['answer']?.toString() ?? '',
    );
  }
}
