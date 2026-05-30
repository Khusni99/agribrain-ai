import 'package:flutter/foundation.dart';

class EnvConfig {
  static const String apiPrefix = '/api/v1';
  static const String appName = 'AgriBrain AI';
  static const Duration connectTimeout = Duration(seconds: 15);
  static const Duration receiveTimeout = Duration(seconds: 30);

  /// Override via: --dart-define=API_BASE_URL=https://api.agribrain.ai
  static String get baseUrl {
    const fromDefine = String.fromEnvironment(
      'API_BASE_URL',
      defaultValue: '',
    );
    if (fromDefine.isNotEmpty) return fromDefine;

    if (kReleaseMode) {
      throw AssertionError(
        'Release mode requires --dart-define=API_BASE_URL=<url>',
      );
    }
    return 'http://10.0.2.2:8000';
  }

  static String get apiBaseUrl => '$baseUrl$apiPrefix';

  static bool get isProduction =>
      kReleaseMode || baseUrl.startsWith('https://');
}
