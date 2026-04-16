import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/question.dart';
import '../models/highscore.dart';
import '../utils/exceptions.dart'; // Import custom exceptions

class ApiService {
  final String baseUrl;

  ApiService(this.baseUrl);

  Future<Question> getQuestion(String category, String difficulty) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/question'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'category': category, 'difficulty': difficulty}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body)['data'];
        return Question.fromJson(data);
      } else {
        throw ServerException('Failed to load question: ${response.statusCode}');
      }
    } catch (e) {
      if (e is ServerException) rethrow;
      throw NetworkException('Network error while fetching question: $e');
    }
  }

  Future<List<Highscore>> getLeaderboard({String? category, String? difficulty, int? limit}) async {
    try {
      final queryParams = {
        if (category != null) 'category': category,
        if (difficulty != null) 'difficulty': difficulty,
        if (limit != null) 'limit': limit.toString(),
      };
      
      final uri = Uri.parse('$baseUrl/api/leaderboard').replace(queryParameters: queryParams);
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        final List data = jsonDecode(response.body)['data']['leaderboard'];
        return data.map((item) => Highscore.fromJson(item)).toList();
      } else {
        throw ServerException('Failed to load leaderboard: ${response.statusCode}');
      }
    } catch (e) {
      if (e is ServerException) rethrow;
      throw NetworkException('Network error while fetching leaderboard: $e');
    }
  }

  Future<void> postScore({
    required String playerName,
    required int score,
    required String category,
    required String difficulty,
    double? timeTaken,
    int? questionsAttempted,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/score'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'player_name': playerName,
          'score': score,
          'category': category,
          'difficulty': difficulty,
          'time_taken': timeTaken,
          'questions_attempted': questionsAttempted,
        }),
      );

      if (response.statusCode != 201) {
        throw ServerException('Failed to post score: ${response.statusCode}');
      }
    } catch (e) {
      if (e is ServerException) rethrow;
      throw NetworkException('Network error while posting score: $e');
    }
  }
}
