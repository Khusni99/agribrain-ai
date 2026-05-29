import 'user_model.dart';

class AuthResponseModel {
  final String accessToken;
  final String tokenType;
  final UserModel user;

  AuthResponseModel({
    required this.accessToken,
    required this.tokenType,
    required this.user,
  });

  factory AuthResponseModel.fromJson(Map<String, dynamic> json) {
    return AuthResponseModel(
      accessToken: json['access_token'],
      tokenType: json['token_type'],
      user: UserModel.fromJson(json['user']),
    );
  }
}
