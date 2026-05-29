import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../farm/providers/farm_provider.dart';
import '../../../data/models/farm_model.dart';
import '../../../core/theme/app_theme.dart';

class ReminderScreen extends ConsumerWidget {
  final int farmId;

  const ReminderScreen({super.key, required this.farmId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final remindersAsync = ref.watch(farmRemindersProvider(farmId));

    return Scaffold(
      appBar: AppBar(title: const Text('Pengingat')),
      body: remindersAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (tasks) {
          if (tasks.isEmpty) {
            return Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.notifications_none, size: 64, color: Colors.grey.shade400),
                  const SizedBox(height: 16),
                  Text('Tidak ada pengingat', style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 8),
                  Text('Semua tugas terselesaikan', style: TextStyle(color: Colors.grey.shade600)),
                ],
              ),
            );
          }
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: tasks.length,
            itemBuilder: (_, i) {
              final t = tasks[i];
              return _ReminderCard(task: t);
            },
          );
        },
      ),
    );
  }
}

class _ReminderCard extends StatelessWidget {
  final UpcomingTaskModel task;

  const _ReminderCard({required this.task});

  @override
  Widget build(BuildContext context) {
    final iconMap = <String, IconData>{
      'panen': Icons.calendar_view_week,
      'semprot': Icons.water_drop,
      'pupuk': Icons.eco,
    };
    final colorMap = <String, Color>{
      'panen': AppTheme.primaryGreen,
      'semprot': AppTheme.infoBlue,
      'pupuk': AppTheme.accentOrange,
    };
    final priorityColor = task.priority == 'high' ? AppTheme.dangerRed : AppTheme.accentOrange;

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            CircleAvatar(
              backgroundColor: (colorMap[task.taskType] ?? Colors.grey).withAlpha(30),
              child: Icon(iconMap[task.taskType] ?? Icons.notifications, color: colorMap[task.taskType]),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(task.title, style: const TextStyle(fontWeight: FontWeight.bold)),
                  if (task.fieldName != null)
                    Text(task.fieldName!, style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(
                          color: priorityColor.withAlpha(30),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          task.priority == 'high' ? 'Segera' : 'Sedang',
                          style: TextStyle(fontSize: 11, color: priorityColor, fontWeight: FontWeight.w600),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'Sisa ${task.daysRemaining} hari',
                        style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            IconButton(
              icon: const Icon(Icons.check_circle_outline, color: AppTheme.primaryGreen),
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Ditandai selesai')),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}
