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
    String? roomId,
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
          'room_id': roomId,
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

  Future<Map<String, dynamic>> createRoom({
    required String playerName,
    required String category,
    required String difficulty,
    String mode = 'time',
    int modeValue = 20,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/multiplayer/create'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'player_name': playerName,
          'category': category,
          'difficulty': difficulty,
          'mode': mode,
          'mode_value': modeValue,
        }),
      );

      if (response.statusCode == 201) {
        return jsonDecode(response.body)['data'];
      } else {
        throw ServerException('Failed to create room: ${response.statusCode}');
      }
    } catch (e) {
      if (e is ServerException) rethrow;
      throw NetworkException('Network error while creating room: $e');
    }
  }

  Future<Map<String, dynamic>> joinRoom({
    required String roomId,
    required String playerName,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl/api/multiplayer/join/$roomId').replace(queryParameters: {'player_name': playerName});
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        return jsonDecode(response.body)['data'];
      } else {
        final errorData = jsonDecode(response.body);
        throw ServerException(errorData['message'] ?? 'Failed to join room: ${response.statusCode}');
      }
    } catch (e) {
      if (e is ServerException) rethrow;
      throw NetworkException('Network error while joining room: $e');
    }
  }

  // New method to fetch available rooms
  Future<List<Map<String, dynamic>>> getAvailableRooms() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/api/multiplayer/rooms'));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body)['data']['rooms'];
        // Ensure data is a list, handle cases where it might be null or not a list
        if (data is List) {
          return List<Map<String, dynamic>>.from(data);
        } else {
          // If data is null or not a list, return empty list
          return [];
        }
      } else {
        throw ServerException('Failed to fetch available rooms: ${response.statusCode}');
      }
    } catch (e) {
      if (e is ServerException) rethrow;
      throw NetworkException('Network error while fetching available rooms: $e');
    }
  }

  // New method to fetch game results
  Future<Map<String, int>> getGameResults(String roomId) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/api/multiplayer/results/$roomId'));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body)['data']['results'];
        // Ensure the scores are integers, handle potential null or non-integer values
        Map<String, int> results = {};
        if (data is Map) {
          data.forEach((key, value) {
            results[key.toString()] = int.tryParse(value.toString()) ?? 0;
          });
        }
        return results;
      } else {
        throw ServerException('Failed to fetch game results: ${response.statusCode}');
      }
    } catch (e) {
      if (e is ServerException) rethrow;
      throw NetworkException('Network error while fetching game results: $e');
    }
  }
}
