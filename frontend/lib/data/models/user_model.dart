class UserModel {
  final int id;
  final String email;
  final String username;
  final String? fullName;
  final String? phone;
  final String role;
  final bool isActive;
  final String language;
  final String createdAt;

  UserModel({
    required this.id,
    required this.email,
    required this.username,
    this.fullName,
    this.phone,
    required this.role,
    required this.isActive,
    required this.language,
    required this.createdAt,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'],
      email: json['email'],
      username: json['username'],
      fullName: json['full_name'],
      phone: json['phone'],
      role: json['role'],
      isActive: json['is_active'],
      language: json['language'],
      createdAt: json['created_at'],
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'email': email,
        'username': username,
        'full_name': fullName,
        'phone': phone,
        'role': role,
        'is_active': isActive,
        'language': language,
        'created_at': createdAt,
      };
}
