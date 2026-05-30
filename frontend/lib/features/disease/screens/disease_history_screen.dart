import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../providers/disease_provider.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/utils/formatters.dart';

class DiseaseHistoryScreen extends ConsumerStatefulWidget {
  const DiseaseHistoryScreen({super.key});

  @override
  ConsumerState<DiseaseHistoryScreen> createState() => _DiseaseHistoryScreenState();
}

class _DiseaseHistoryScreenState extends ConsumerState<DiseaseHistoryScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() => ref.read(diseaseProvider.notifier).loadHistory());
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(diseaseProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Riwayat Deteksi')),
      body: state.historyLoading
          ? const Center(child: CircularProgressIndicator())
          : state.history.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.history,
                          size: 64,
                          color: theme.colorScheme.onSurfaceVariant.withAlpha(100)),
                      const SizedBox(height: 12),
                      Text('Belum ada riwayat deteksi',
                          style: theme.textTheme.bodyLarge),
                      const SizedBox(height: 4),
                      Text('Deteksi penyakit tanaman untuk memulai',
                          style: theme.textTheme.bodySmall
                              ?.copyWith(color: Colors.grey)),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: () async =>
                      ref.read(diseaseProvider.notifier).loadHistory(),
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: state.history.length,
                    itemBuilder: (_, i) {
                      final item = state.history[i];
                      final riskColor = item.economicRisk.riskLevel == 'TINGGI'
                          ? AppTheme.dangerRed
                          : item.economicRisk.riskLevel == 'SEDANG'
                              ? AppTheme.accentOrange
                              : AppTheme.primaryGreen;
                      return Card(
                        margin: const EdgeInsets.only(bottom: 12),
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              if (item.imageUrl != null) ...[
                                ClipRRect(
                                  borderRadius: BorderRadius.circular(12),
                                  child: CachedNetworkImage(
                                    imageUrl: item.imageUrl!,
                                    height: 160,
                                    width: double.infinity,
                                    fit: BoxFit.cover,
                                    placeholder: (_, __) => Container(
                                      height: 160,
                                      color: theme.colorScheme.surfaceContainerHighest,
                                    ),
                                    errorWidget: (_, __, ___) => Container(
                                      height: 160,
                                      color: theme.colorScheme.surfaceContainerHighest,
                                      child: const Icon(Icons.broken_image),
                                    ),
                                  ),
                                ),
                                const SizedBox(height: 12),
                              ],
                              Row(
                                children: [
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                        horizontal: 8, vertical: 4),
                                    decoration: BoxDecoration(
                                      color: riskColor.withAlpha(20),
                                      borderRadius: BorderRadius.circular(8),
                                    ),
                                    child: Text(
                                      item.diseaseName,
                                      style: TextStyle(
                                        fontWeight: FontWeight.bold,
                                        color: riskColor,
                                        fontSize: 13,
                                      ),
                                    ),
                                  ),
                                  const Spacer(),
                                  Text(
                                    Formatters.date(item.createdAt ?? ''),
                                    style: const TextStyle(
                                        fontSize: 11, color: Colors.grey),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 8),
                              Row(
                                children: [
                                  _StatChip(
                                    label: 'Tingkat',
                                    value: '${item.severity.toStringAsFixed(0)}%',
                                    color: riskColor,
                                  ),
                                  const SizedBox(width: 8),
                                  _StatChip(
                                    label: 'Keyakinan',
                                    value:
                                        '${(item.confidence * 100).toStringAsFixed(0)}%',
                                    color: AppTheme.infoBlue,
                                  ),
                                  const SizedBox(width: 8),
                                  _StatChip(
                                    label: 'Risiko',
                                    value: item.economicRisk.riskLevel,
                                    color: riskColor,
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
    );
  }
}

class _StatChip extends StatelessWidget {
  final String label;
  final String value;
  final Color color;

  const _StatChip({
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 8),
        decoration: BoxDecoration(
          color: color.withAlpha(15),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Column(
          children: [
            Text(
              value,
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 14,
                color: color,
              ),
            ),
            Text(
              label,
              style: const TextStyle(fontSize: 10, color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }
}
