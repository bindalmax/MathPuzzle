import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:google_sign_in/google_sign_in.dart';
import '../services/api_service.dart';

class AuthProvider with ChangeNotifier {
  final ApiService apiService;
  final dynamic _googleSignIn; // Using dynamic to bypass weird compilation issues during testing

  int? _userId;
  String? _displayName;
  String? _email;
  bool _isLoading = false;
  String? _error;

  AuthProvider({
    required this.apiService,
    dynamic googleSignIn,
  }) : _googleSignIn = googleSignIn {
    _loadUser();
  }

  int? get userId => _userId;
  String? get displayName => _displayName;
  String? get email => _email;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get isAuthenticated => _userId != null;

  Future<void> _loadUser() async {
    final prefs = await SharedPreferences.getInstance();
    _userId = prefs.getInt('auth_user_id');
    _displayName = prefs.getString('auth_display_name');
    _email = prefs.getString('auth_email');
    notifyListeners();
  }

  Future<bool> signInWithGoogle() async {
    if (_googleSignIn == null) {
      _error = 'Google Sign-In is not configured.';
      notifyListeners();
      return false;
    }

    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      // ignore: avoid_dynamic_calls
      final googleUser = await _googleSignIn.signIn();
      if (googleUser == null) {
        _isLoading = false;
        notifyListeners();
        return false; // User cancelled
      }

      // ignore: avoid_dynamic_calls
      final googleAuth = await googleUser.authentication;
      final String? idToken = googleAuth.idToken;

      if (idToken == null) {
        throw Exception('Failed to get ID Token from Google');
      }

      // Authenticate with backend
      final data = await apiService.authenticateGoogle(idToken);
      
      _userId = data['user_id'];
      _displayName = data['display_name'];
      _email = data['email'];

      // Persist locally
      final prefs = await SharedPreferences.getInstance();
      await prefs.setInt('auth_user_id', _userId!);
      await prefs.setString('auth_display_name', _displayName!);
      await prefs.setString('auth_email', _email!);

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = 'Google Sign-In failed: $e';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<void> signOut() async {
    if (_googleSignIn != null) {
      try {
        // ignore: avoid_dynamic_calls
        await _googleSignIn.signOut();
      } catch (_) {}
    }
    
    _userId = null;
    _displayName = null;
    _email = null;

    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_user_id');
    await prefs.remove('auth_display_name');
    await prefs.remove('auth_email');
    
    notifyListeners();
  }
}
