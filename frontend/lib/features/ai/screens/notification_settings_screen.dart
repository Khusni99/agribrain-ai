import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../data/repositories/notification_repository.dart';
import '../../../data/models/notification_model.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/widgets/agri_card.dart';
import '../../../core/widgets/loading_view.dart';
import '../../../core/widgets/error_view.dart';

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
        loading: () => const LoadingView(message: 'Memuat pengaturan...'),
        error: (e, _) => ErrorView(message: 'Gagal memuat: $e', onRetry: () => ref.invalidate(reminderPreferencesProvider)),
        data: (prefs) => ListView(
          padding: const EdgeInsets.all(16),
          children: [
            AgriCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: AppTheme.whatsappGreen.withAlpha(25),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: const Icon(Icons.chat, color: AppTheme.whatsappGreen, size: 20),
                      ),
                      const SizedBox(width: 12),
                      Text('Notifikasi WhatsApp', style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
                    ],
                  ),
                  const SizedBox(height: 8),
                  SwitchListTile(
                    title: const Text('Aktifkan Notifikasi WhatsApp'),
                    subtitle: const Text('Terima pengingat melalui WhatsApp'),
                    value: prefs.whatsappEnabled,
                    onChanged: (v) => _update({'whatsapp_enabled': v}),
                    contentPadding: EdgeInsets.zero,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
            AgriCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: AppTheme.accentOrange.withAlpha(25),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: const Icon(Icons.notifications_active, color: AppTheme.accentOrange, size: 20),
                      ),
                      const SizedBox(width: 12),
                      Text('Jenis Pengingat', style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
                    ],
                  ),
                  const SizedBox(height: 8),
                  SwitchListTile(
                    title: const Text('Pengingat Pemupukan'),
                    subtitle: Text('${prefs.advanceDaysFertilizer} hari sebelum jadwal'),
                    value: prefs.fertilizerReminder,
                    onChanged: (v) => _update({'fertilizer_reminder': v}),
                    contentPadding: EdgeInsets.zero,
                  ),
                  const Divider(height: 1),
                  SwitchListTile(
                    title: const Text('Pengingat Penyemprotan'),
                    subtitle: Text('${prefs.advanceDaysSpray} hari sebelum jadwal'),
                    value: prefs.sprayReminder,
                    onChanged: (v) => _update({'spray_reminder': v}),
                    contentPadding: EdgeInsets.zero,
                  ),
                  const Divider(height: 1),
                  SwitchListTile(
                    title: const Text('Pengingat Panen'),
                    subtitle: Text('${prefs.advanceDaysHarvest} hari sebelum panen'),
                    value: prefs.harvestReminder,
                    onChanged: (v) => _update({'harvest_reminder': v}),
                    contentPadding: EdgeInsets.zero,
                  ),
                  const Divider(height: 1),
                  SwitchListTile(
                    title: const Text('Peringatan Risiko Penyakit'),
                    subtitle: const Text('Deteksi risiko penyakit tanaman'),
                    value: prefs.diseaseRiskAlert,
                    onChanged: (v) => _update({'disease_risk_alert': v}),
                    contentPadding: EdgeInsets.zero,
                  ),
                  const Divider(height: 1),
                  SwitchListTile(
                    title: const Text('Peringatan Cuaca'),
                    subtitle: const Text('Info cuaca ekstrem'),
                    value: prefs.weatherAlert,
                    onChanged: (v) => _update({'weather_alert': v}),
                    contentPadding: EdgeInsets.zero,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
            AgriCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: AppTheme.infoBlue.withAlpha(25),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: const Icon(Icons.schedule, color: AppTheme.infoBlue, size: 20),
                      ),
                      const SizedBox(width: 12),
                      Text('Waktu Notifikasi', style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
                    ],
                  ),
                  const SizedBox(height: 8),
                  ListTile(
                    title: const Text('Mulai'),
                    trailing: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                      decoration: BoxDecoration(
                        color: AppTheme.primaryGreen.withAlpha(15),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(prefs.reminderTimeStart, style: const TextStyle(fontWeight: FontWeight.bold, color: AppTheme.primaryGreen)),
                    ),
                    contentPadding: EdgeInsets.zero,
                  ),
                  ListTile(
                    title: const Text('Selesai'),
                    trailing: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                      decoration: BoxDecoration(
                        color: AppTheme.dangerRed.withAlpha(15),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(prefs.reminderTimeEnd, style: const TextStyle(fontWeight: FontWeight.bold, color: AppTheme.dangerRed)),
                    ),
                    contentPadding: EdgeInsets.zero,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
            AgriCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: Colors.grey.withAlpha(30),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: const Icon(Icons.history, color: Colors.grey, size: 20),
                      ),
                      const SizedBox(width: 12),
                      Text('Riwayat Notifikasi', style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Consumer(
                    builder: (_, ref, __) {
                      final notifAsync = FutureProvider.autoDispose((ref) async {
                        return ref.read(notificationRepositoryProvider).getNotifications(limit: 5);
                      });
                      return ref.watch(notifAsync).when(
                        loading: () => const LoadingView(message: 'Memuat riwayat...'),
                        error: (e, _) => Text('Gagal memuat: $e', style: const TextStyle(color: Colors.grey)),
                        data: (list) {
                          if (list.isEmpty) {
                            return const Padding(
                              padding: EdgeInsets.symmetric(vertical: 16),
                              child: Center(child: Text('Belum ada notifikasi', style: TextStyle(color: Colors.grey))),
                            );
                          }
                          return Column(
                            children: list.map((n) => ListTile(
                              dense: true,
                              leading: CircleAvatar(
                                radius: 16,
                                backgroundColor: AppTheme.infoBlue.withAlpha(25),
                                child: Icon(_notifIcon(n.notificationType), size: 16, color: AppTheme.infoBlue),
                              ),
                              title: Text(n.title, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500)),
                              subtitle: Text(n.message, style: const TextStyle(fontSize: 11), maxLines: 1),
                              trailing: Text(
                                n.sentAt.length >= 10 ? n.sentAt.substring(0, 10) : '',
                                style: TextStyle(fontSize: 10, color: Colors.grey.shade600),
                              ),
                              contentPadding: EdgeInsets.zero,
                            )).toList(),
                          );
                        },
                      );
                    },
                  ),
                ],
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
