import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../data/repositories/notification_repository.dart';
import '../../../data/models/notification_model.dart';
import '../../../core/theme/app_theme.dart';

final reminderPreferencesProvider = FutureProvider.autoDispose<ReminderPreferenceModel>((ref) async {
  return ref.read(notificationRepositoryProvider).getPreferences();
});

class NotificationSettingsScreen extends ConsumerStatefulWidget {
  const NotificationSettingsScreen({super.key});

  @override
  ConsumerState<NotificationSettingsScreen> createState() => _NotificationSettingsScreenState();
}

class _NotificationSettingsScreenState extends ConsumerState<NotificationSettingsScreen> {

  Future<void> _update(Map<String, dynamic> data) async {
    try {
      await ref.read(notificationRepositoryProvider).updatePreferences(data);
      ref.invalidate(reminderPreferencesProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Pengaturan tersimpan')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Gagal: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final prefsAsync = ref.watch(reminderPreferencesProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Pengaturan Notifikasi')),
      body: prefsAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (prefs) => ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Notifikasi WhatsApp', style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    SwitchListTile(
                      title: const Text('Aktifkan Notifikasi WhatsApp'),
                      subtitle: const Text('Terima pengingat melalui WhatsApp'),
                      value: prefs.whatsappEnabled,
                      onChanged: (v) => _update({'whatsapp_enabled': v}),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Jenis Pengingat', style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    SwitchListTile(
                      title: const Text('Pengingat Pemupukan'),
                      subtitle: Text('${prefs.advanceDaysFertilizer} hari sebelum jadwal'),
                      value: prefs.fertilizerReminder,
                      onChanged: (v) => _update({'fertilizer_reminder': v}),
                    ),
                    SwitchListTile(
                      title: const Text('Pengingat Penyemprotan'),
                      subtitle: Text('${prefs.advanceDaysSpray} hari sebelum jadwal'),
                      value: prefs.sprayReminder,
                      onChanged: (v) => _update({'spray_reminder': v}),
                    ),
                    SwitchListTile(
                      title: const Text('Pengingat Panen'),
                      subtitle: Text('${prefs.advanceDaysHarvest} hari sebelum panen'),
                      value: prefs.harvestReminder,
                      onChanged: (v) => _update({'harvest_reminder': v}),
                    ),
                    SwitchListTile(
                      title: const Text('Peringatan Risiko Penyakit'),
                      subtitle: const Text('Deteksi risiko penyakit tanaman'),
                      value: prefs.diseaseRiskAlert,
                      onChanged: (v) => _update({'disease_risk_alert': v}),
                    ),
                    SwitchListTile(
                      title: const Text('Peringatan Cuaca'),
                      subtitle: const Text('Info cuaca ekstrem'),
                      value: prefs.weatherAlert,
                      onChanged: (v) => _update({'weather_alert': v}),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Waktu Notifikasi', style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    ListTile(
                      title: const Text('Mulai'),
                      trailing: Text(prefs.reminderTimeStart, style: const TextStyle(fontWeight: FontWeight.bold)),
                    ),
                    ListTile(
                      title: const Text('Selesai'),
                      trailing: Text(prefs.reminderTimeEnd, style: const TextStyle(fontWeight: FontWeight.bold)),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Riwayat Notifikasi', style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    Consumer(
                      builder: (_, ref, __) {
                        final notifAsync = FutureProvider.autoDispose((ref) async {
                          return ref.read(notificationRepositoryProvider).getNotifications(limit: 5);
                        });
                        return ref.watch(notifAsync).when(
                          loading: () => const Center(child: CircularProgressIndicator()),
                          error: (e, _) => Text('Gagal memuat: $e'),
                          data: (list) {
                            if (list.isEmpty) return const Text('Belum ada notifikasi', style: TextStyle(color: Colors.grey));
                            return Column(
                              children: list.map((n) => ListTile(
                                dense: true,
                                leading: Icon(_notifIcon(n.notificationType), size: 20, color: AppTheme.infoBlue),
                                title: Text(n.title, style: const TextStyle(fontSize: 13)),
                                subtitle: Text(n.message, style: const TextStyle(fontSize: 11), maxLines: 1),
                                trailing: Text(n.sentAt.length >= 10 ? n.sentAt.substring(0, 10) : '', style: TextStyle(fontSize: 10, color: Colors.grey.shade600)),
                              )).toList(),
                            );
                          },
                        );
                      },
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  IconData _notifIcon(String type) {
    switch (type) {
      case 'fertilizer': return Icons.science;
      case 'spray': return Icons.water_drop;
      case 'harvest': return Icons.calendar_month;
      case 'disease': return Icons.warning_amber;
      default: return Icons.notifications;
    }
  }
}
