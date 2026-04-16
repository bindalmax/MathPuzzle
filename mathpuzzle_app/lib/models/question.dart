class Question {
  final String id;
  final String text;
  final List<String> choices;
  final String correctAnswer;

  Question({required this.id, required this.text, this.choices = const [], required this.correctAnswer});

  factory Question.fromJson(Map<String, dynamic> json) {
    // Map choices to String list, handling potential nulls or integer values
    var choicesJson = json['choices'] as List?;
    List<String> parsedChoices = choicesJson != null 
        ? choicesJson.map((choice) => choice.toString()).toList() 
        : [];

    return Question(
      id: json['question_id']?.toString() ?? '',
      text: json['question']?.toString() ?? '',
      choices: parsedChoices,
      correctAnswer: json['answer']?.toString() ?? '',
    );
  }
}
