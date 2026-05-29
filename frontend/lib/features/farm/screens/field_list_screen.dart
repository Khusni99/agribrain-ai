import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/farm_provider.dart';
import '../../../data/models/farm_model.dart';
import '../../../core/theme/app_theme.dart';
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
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (fields) {
          if (fields.isEmpty) {
            return Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.grid_view, size: 64, color: Colors.grey.shade400),
                  const SizedBox(height: 16),
                  Text('Belum ada petak', style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 24),
                  ElevatedButton.icon(
                    onPressed: () => _openFieldForm(context, ref),
                    icon: const Icon(Icons.add),
                    label: const Text('Tambah Petak'),
                  ),
                ],
              ),
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
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: field.status == 'active' ? AppTheme.primaryGreen.withAlpha(30) : Colors.grey.shade200,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      field.status == 'active' ? 'Aktif' : 'Nonaktif',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                        color: field.status == 'active' ? AppTheme.primaryGreen : Colors.grey.shade700,
                      ),
                    ),
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
