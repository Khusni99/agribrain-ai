import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/farm_provider.dart';
import '../../../data/models/farm_model.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/widgets/loading_view.dart';
import '../../../core/widgets/error_view.dart';
import '../../../core/widgets/empty_state.dart';
import '../../../core/widgets/status_badge.dart';
import 'field_form_screen.dart';
import '../../dashboard/screens/dashboard_screen.dart';

class FieldListScreen extends ConsumerWidget {
  final FarmModel farm;

  const FieldListScreen({super.key, required this.farm});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final fieldsAsync = ref.watch(farmFieldsProvider(farm.id));

    return Scaffold(
      appBar: AppBar(
        title: Text(farm.name),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => _openFieldForm(context, ref),
          ),
        ],
      ),
      body: fieldsAsync.when(
        loading: () => const LoadingView(message: 'Memuat petak...'),
        error: (e, _) => ErrorView(
          message: 'Gagal memuat petak: $e',
          onRetry: () => ref.invalidate(farmFieldsProvider(farm.id)),
        ),
        data: (fields) {
          if (fields.isEmpty) {
            return Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                EmptyState(
                  icon: Icons.grid_view,
                  title: 'Belum ada petak',
                  subtitle: 'Tambahkan petak untuk lahan ${farm.name}',
                ),
                const SizedBox(height: 8),
                FilledButton.icon(
                  onPressed: () => _openFieldForm(context, ref),
                  icon: const Icon(Icons.add),
                  label: const Text('Tambah Petak'),
                ),
              ],
            );
          }
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              _FarmSummaryCard(farm: farm),
              const SizedBox(height: 16),
              ...fields.map((f) => _FieldCard(field: f, farmId: farm.id)),
            ],
          );
        },
      ),
    );
  }

  void _openFieldForm(BuildContext context, WidgetRef ref) {
    Navigator.push(context, MaterialPageRoute(
      builder: (_) => FieldFormScreen(farmId: farm.id),
    ));
  }
}

class _FarmSummaryCard extends StatelessWidget {
  final FarmModel farm;

  const _FarmSummaryCard({required this.farm});

  @override
  Widget build(BuildContext context) {
    return Card(
      color: AppTheme.surfaceLight,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(farm.name, style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            if (farm.location != null) Text('📍 ${farm.location}', style: const TextStyle(color: Colors.grey)),
            if (farm.soilType != null) Text('🧑‍🌾 Tanah: ${farm.soilType}', style: const TextStyle(color: Colors.grey)),
            if (farm.description != null) Text('📝 ${farm.description}', style: const TextStyle(color: Colors.grey)),
          ],
        ),
      ),
    );
  }
}

class _FieldCard extends StatelessWidget {
  final FieldModel field;
  final int farmId;

  const _FieldCard({required this.field, required this.farmId});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: () => Navigator.push(context, MaterialPageRoute(
          builder: (_) => DashboardScreen(farmId: farmId, fieldId: field.id, fieldName: field.name),
        )),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: field.status == 'active' ? AppTheme.cardGreen : Colors.grey.shade100,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Icon(
                      field.status == 'active' ? Icons.check_circle : Icons.pause_circle,
                      color: field.status == 'active' ? AppTheme.primaryGreen : Colors.grey,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(field.name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                        if (field.cropType != null)
                          Text(field.cropType!, style: TextStyle(color: Colors.grey.shade600, fontSize: 13)),
                      ],
                    ),
                  ),
                  StatusBadge(
                    label: field.status == 'active' ? 'Aktif' : 'Nonaktif',
                    color: field.status == 'active' ? AppTheme.primaryGreen : Colors.grey,
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  _chip(Icons.straighten, '${field.areaHectare?.toStringAsFixed(1) ?? "-"} Ha'),
                  const SizedBox(width: 12),
                  _chip(Icons.calendar_today, field.plantingDate != null ? field.plantingDate!.substring(0, 10) : '-'),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _chip(IconData icon, String label) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 14, color: Colors.grey.shade600),
        const SizedBox(width: 4),
        Text(label, style: TextStyle(fontSize: 12, color: Colors.grey.shade700)),
      ],
    );
  }
}
