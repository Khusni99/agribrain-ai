import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../data/repositories/auth_repository.dart';
import '../../../data/models/user_model.dart';

enum AuthStatus { initial, loading, authenticated, unauthenticated, error }

class AuthState {
  final AuthStatus status;
  final String? error;
  final UserModel? user;

  const AuthState({this.status = AuthStatus.initial, this.error, this.user});

  AuthState copyWith({AuthStatus? status, String? error, UserModel? user}) {
    return AuthState(
      status: status ?? this.status,
      error: error,
      user: user ?? this.user,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  final AuthRepository _repo;

  AuthNotifier(this._repo) : super(const AuthState()) {
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    final loggedIn = await _repo.isLoggedIn();
    if (loggedIn) {
      state = state.copyWith(status: AuthStatus.authenticated);
    } else {
      state = state.copyWith(status: AuthStatus.unauthenticated);
    }
  }

  Future<void> register(String email, String username, String password,
      {String? fullName, String? phone}) async {
    state = state.copyWith(status: AuthStatus.loading);
    try {
      final auth = await _repo.register(email, username, password,
          fullName: fullName, phone: phone);
      state = state.copyWith(
        status: AuthStatus.authenticated,
        user: auth.user,
      );
    } catch (e) {
      state = state.copyWith(status: AuthStatus.error, error: _formatError(e));
    }
  }

  Future<void> login(String username, String password) async {
    state = state.copyWith(status: AuthStatus.loading);
    try {
      final auth = await _repo.login(username, password);
      state = state.copyWith(
        status: AuthStatus.authenticated,
        user: auth.user,
      );
    } catch (e) {
      state = state.copyWith(status: AuthStatus.error, error: _formatError(e));
    }
  }

  Future<void> logout() async {
    await _repo.logout();
    state = const AuthState(status: AuthStatus.unauthenticated);
  }

  String _formatError(Object e) {
    final msg = e.toString();
    if (msg.contains('Invalid credentials')) return 'Email atau password salah';
    if (msg.contains('already registered')) return 'Email atau username sudah terdaftar';
    return 'Terjadi kesalahan. Silakan coba lagi.';
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.read(authRepositoryProvider));
});
