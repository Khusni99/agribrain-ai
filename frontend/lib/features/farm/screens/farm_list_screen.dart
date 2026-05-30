import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/farm_provider.dart';
import '../../../data/models/farm_model.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/widgets/loading_view.dart';
import '../../../core/widgets/error_view.dart';
import '../../../core/widgets/empty_state.dart';
import 'farm_form_screen.dart';
import 'field_list_screen.dart';

class FarmListScreen extends ConsumerWidget {
  const FarmListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final farmsAsync = ref.watch(farmsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Lahan Saya'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => _openForm(context, ref),
          ),
        ],
      ),
      body: farmsAsync.when(
        loading: () => const LoadingView(message: 'Memuat lahan...'),
        error: (e, _) => ErrorView(
          message: 'Gagal memuat data',
          onRetry: () => ref.read(farmsProvider.notifier).load(),
        ),
        data: (farms) {
          if (farms.isEmpty) {
            return Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                EmptyState(
                  icon: Icons.agriculture,
                  title: 'Belum ada lahan',
                  subtitle: 'Tambahkan lahan pertama Anda',
                ),
                const SizedBox(height: 8),
                FilledButton.icon(
                  onPressed: () => _openForm(context, ref),
                  icon: const Icon(Icons.add),
                  label: const Text('Tambah Lahan'),
                ),
              ],
            );
          }
          return RefreshIndicator(
            onRefresh: () => ref.read(farmsProvider.notifier).load(),
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: farms.length,
              itemBuilder: (_, i) => _FarmCard(farm: farms[i], ref: ref),
            ),
          );
        },
      ),
    );
  }

  void _openForm(BuildContext context, WidgetRef ref) {
    Navigator.push(context, MaterialPageRoute(
      builder: (_) => const FarmFormScreen(),
    ));
  }
}

class _FarmCard extends StatelessWidget {
  final FarmModel farm;
  final WidgetRef ref;

  const _FarmCard({required this.farm, required this.ref});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: () => Navigator.push(context, MaterialPageRoute(
          builder: (_) => FieldListScreen(farm: farm),
        )),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: AppTheme.primaryGreen.withAlpha(30),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Icon(Icons.agriculture, color: AppTheme.primaryGreen),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(farm.name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                        if (farm.location != null)
                          Text(farm.location!, style: TextStyle(color: Colors.grey.shade600, fontSize: 13)),
                      ],
                    ),
                  ),
                  PopupMenuButton<String>(
                    onSelected: (v) {
                      if (v == 'edit') {
                        Navigator.push(context, MaterialPageRoute(
                          builder: (_) => FarmFormScreen(farm: farm),
                        ));
                      } else if (v == 'delete') {
                        _deleteFarm(context);
                      }
                    },
                    itemBuilder: (_) => [
                      const PopupMenuItem(value: 'edit', child: Row(children: [Icon(Icons.edit, size: 18), SizedBox(width: 8), Text('Edit')])),
                      const PopupMenuItem(value: 'delete', child: Row(children: [Icon(Icons.delete, size: 18, color: Colors.red), SizedBox(width: 8), Text('Hapus', style: TextStyle(color: Colors.red))])),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  _InfoChip(icon: Icons.straighten, label: '${farm.areaHectare?.toStringAsFixed(1) ?? "-"} Ha'),
                  const SizedBox(width: 12),
                  _InfoChip(icon: Icons.grid_view, label: '${farm.fieldsCount} Petak'),
                  const SizedBox(width: 12),
                  if (farm.soilType != null)
                    _InfoChip(icon: Icons.layers, label: farm.soilType!),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _deleteFarm(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Hapus Lahan'),
        content: Text('Yakin ingin menghapus "${farm.name}"?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Batal')),
          TextButton(
            onPressed: () {
              Navigator.pop(ctx);
              ref.read(farmsProvider.notifier).delete(farm.id);
            },
            child: const Text('Hapus', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  final IconData icon;
  final String label;

  const _InfoChip({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
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
