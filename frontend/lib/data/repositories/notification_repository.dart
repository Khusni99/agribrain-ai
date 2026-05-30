import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/notification_model.dart';
import '../../core/network/api_client.dart';

final notificationRepositoryProvider = Provider<NotificationRepository>((ref) {
  return NotificationRepository(ref.read(apiClientProvider));
});

class NotificationRepository {
  final ApiClient _client;

  NotificationRepository(this._client);

  Future<List<NotificationLogModel>> getNotifications({int limit = 20}) async {
    final response = await _client.get('/notifications/', queryParams: {'limit': limit});
    return (response.data as List).map((e) => NotificationLogModel.fromJson(e)).toList();
  }

  Future<int> getUnreadCount() async {
    final response = await _client.get('/notifications/unread');
    return response.data['unread_count'] as int? ?? 0;
  }

  Future<void> markRead(int id) async {
    await _client.put('/notifications/$id/read');
  }

  Future<ReminderPreferenceModel> getPreferences() async {
    final response = await _client.get('/notifications/preferences');
    return ReminderPreferenceModel.fromJson(response.data);
  }

  Future<ReminderPreferenceModel> updatePreferences(Map<String, dynamic> data) async {
    final response = await _client.put('/notifications/preferences', data: data);
    return ReminderPreferenceModel.fromJson(response.data);
  }

  Future<Map<String, dynamic>> registerWhatsApp(String phoneNumber) async {
    final response = await _client.post('/whatsapp/register', data: {
      'phone_number': phoneNumber,
    });
    return response.data as Map<String, dynamic>;
  }

  Future<WhatsAppSessionModel> getWhatsAppSession() async {
    final response = await _client.get('/whatsapp/session');
    return WhatsAppSessionModel.fromJson(response.data);
  }
}
