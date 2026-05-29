class EnvConfig {
  static const String baseUrl = 'http://10.0.2.2:8000';
  static const String apiPrefix = '/api/v1';
  static const String appName = 'AgriBrain AI';
  static const Duration connectTimeout = Duration(seconds: 15);
  static const Duration receiveTimeout = Duration(seconds: 30);

  static String get apiBaseUrl => '$baseUrl$apiPrefix';
}
