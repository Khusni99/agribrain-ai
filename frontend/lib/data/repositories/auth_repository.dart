import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/api_client.dart';
import '../../core/storage/secure_storage.dart';
import '../models/auth_response_model.dart';

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(ref.read(apiClientProvider), ref.read(secureStorageProvider));
});

class AuthRepository {
  final ApiClient _api;
  final SecureStorageService _storage;

  AuthRepository(this._api, this._storage);

  Future<AuthResponseModel> register(String email, String username, String password,
      {String? fullName, String? phone}) async {
    final response = await _api.post('/auth/register', data: {
      'email': email,
      'username': username,
      'password': password,
      'full_name': fullName,
      'phone': phone,
    });
    final auth = AuthResponseModel.fromJson(response.data);
    await _storage.saveToken(auth.accessToken);
    await _storage.saveUserData(response.data['user'].toString());
    return auth;
  }

  Future<AuthResponseModel> login(String username, String password) async {
    final response = await _api.post('/auth/login', data: {
      'username': username,
      'password': password,
    });
    final auth = AuthResponseModel.fromJson(response.data);
    await _storage.saveToken(auth.accessToken);
    await _storage.saveUserData(response.data['user'].toString());
    return auth;
  }

  Future<void> logout() async {
    await _storage.clearAll();
  }

  Future<String?> getSavedToken() async {
    return await _storage.getToken();
  }

  Future<bool> isLoggedIn() async {
    final token = await _storage.getToken();
    return token != null && token.isNotEmpty;
  }
}
