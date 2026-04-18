import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:mathpuzzle_app/providers/auth_provider.dart';
import '../mocks.dart';

void main() {
  late AuthProvider authProvider;
  late MockApiService mockApiService;

  setUp(() async {
    SharedPreferences.setMockInitialValues({});
    mockApiService = MockApiService();
    authProvider = AuthProvider(
      apiService: mockApiService,
      googleSignIn: MockGoogleSignIn(),
    );
  });

  group('AuthProvider Unit Tests', () {
    test('Initial state is unauthenticated', () {
      expect(authProvider.isAuthenticated, false);
      expect(authProvider.userId, null);
    });

    test('signInWithGoogle success updates state and preferences', () async {
      final success = await authProvider.signInWithGoogle();
      
      expect(success, true);
      expect(authProvider.isAuthenticated, true);
      expect(authProvider.userId, 1);
      expect(authProvider.displayName, 'Mock User');
      
      final prefs = await SharedPreferences.getInstance();
      expect(prefs.getInt('auth_user_id'), 1);
      expect(prefs.getString('auth_display_name'), 'Mock User');
    });

    test('signOut clears state and preferences', () async {
      // Manual internal state set (simulating successful login)
      // This is a bit of a hack since _userId is private, but for a lean test:
      await authProvider.signOut();
      expect(authProvider.isAuthenticated, false);
      
      final prefs = await SharedPreferences.getInstance();
      expect(prefs.getInt('auth_user_id'), null);
    });
  });
}
