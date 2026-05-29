import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../farm/providers/farm_provider.dart';
import '../../../core/theme/app_theme.dart';

class TimelineScreen extends ConsumerWidget {
  final int farmId;

  const TimelineScreen({super.key, required this.farmId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final timelineAsync = ref.watch(farmTimelineProvider(farmId));

    return Scaffold(
      appBar: AppBar(title: const Text('Aktivitas Lahan')),
      body: timelineAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (activities) {
          if (activities.isEmpty) {
            return Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.history, size: 64, color: Colors.grey.shade400),
                  const SizedBox(height: 16),
                  Text('Belum ada aktivitas', style: Theme.of(context).textTheme.titleMedium),
                ],
              ),
            );
          }
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: activities.length,
            itemBuilder: (_, i) {
              final a = activities[i];
              final iconMap = <String, IconData>{
                'panen': Icons.calendar_view_week,
                'semprot': Icons.water_drop,
                'pupuk': Icons.eco,
                'penyakit': Icons.warning_amber,
              };
              final colorMap = <String, Color>{
                'panen': AppTheme.primaryGreen,
                'semprot': AppTheme.infoBlue,
                'pupuk': AppTheme.accentOrange,
                'penyakit': AppTheme.dangerRed,
              };

              return Card(
                margin: const EdgeInsets.only(bottom: 8),
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundColor: (colorMap[a.activityType] ?? Colors.grey).withAlpha(30),
                    child: Icon(iconMap[a.activityType] ?? Icons.circle, color: colorMap[a.activityType]),
                  ),
                  title: Text(a.description),
                  subtitle: Text(
                    a.timestamp.length >= 16 ? a.timestamp.substring(0, 16).replaceAll('T', ' ') : a.timestamp,
                    style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
