import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/cost_provider.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/utils/formatters.dart';

class CostScreen extends ConsumerWidget {
  const CostScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(costProvider);
    final theme = Theme.of(context);
    final notifier = ref.read(costProvider.notifier);

    return Scaffold(
      appBar: AppBar(title: const Text('Kalkulator Biaya')),
      body: state.result == null ? _buildForm(context, theme, state, notifier) : _buildResult(context, theme, state, notifier),
    );
  }

  Widget _buildForm(BuildContext context, ThemeData theme, CostState state, CostNotifier notifier) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Informasi Lahan', style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          TextFormField(
            initialValue: state.cropType,
            decoration: const InputDecoration(labelText: 'Jenis Tanaman', prefixIcon: Icon(Icons.eco)),
            onChanged: notifier.updateCropType,
          ),
          const SizedBox(height: 12),
          TextFormField(
            initialValue: state.areaHectare.toString(),
            keyboardType: TextInputType.number,
            decoration: const InputDecoration(labelText: 'Luas Lahan (Ha)', prefixIcon: Icon(Icons.straighten)),
            onChanged: (v) => notifier.updateArea(double.tryParse(v) ?? 0),
          ),
          const SizedBox(height: 16),
          Text('Biaya Produksi', style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          ...state.items.asMap().entries.map((entry) {
            final i = entry.key;
            final item = entry.value;
            return Card(
              margin: const EdgeInsets.only(bottom: 8),
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(item.name, style: const TextStyle(fontWeight: FontWeight.w600)),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Expanded(
                          child: TextFormField(
                            initialValue: item.quantity.toString(),
                            keyboardType: TextInputType.number,
                            decoration: InputDecoration(
                              labelText: 'Jumlah',
                              suffixText: item.unit,
                              isDense: true,
                              contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                            ),
                            onChanged: (v) => notifier.updateItem(i, double.tryParse(v) ?? 0, item.unitPrice),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: TextFormField(
                            initialValue: item.unitPrice.toString(),
                            keyboardType: TextInputType.number,
                            decoration: const InputDecoration(
                              labelText: 'Harga',
                              prefixText: 'Rp ',
                              isDense: true,
                              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                            ),
                            onChanged: (v) => notifier.updateItem(i, item.quantity, double.tryParse(v) ?? 0),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            );
          }),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: state.isLoading ? null : () => notifier.calculate(),
            style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primaryGreen, foregroundColor: Colors.white),
            child: state.isLoading
                ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                : const Text('Hitung Biaya', style: TextStyle(fontSize: 16)),
          ),
          if (state.error != null) ...[
            const SizedBox(height: 12),
            Text(state.error!, style: const TextStyle(color: AppTheme.dangerRed)),
          ],
        ],
      ),
    );
  }

  Widget _buildResult(BuildContext context, ThemeData theme, CostState state, CostNotifier notifier) {
    final r = state.result!;
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          Card(
            color: AppTheme.primaryGreen.withAlpha(20),
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  Text('Total Biaya', style: theme.textTheme.bodyMedium?.copyWith(color: Colors.grey)),
                  const SizedBox(height: 4),
                  Text(Formatters.currency(r.totalCost), style: theme.textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold, color: AppTheme.primaryGreen,
                  )),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(child: _StatCard(label: 'Biaya/Tanaman', value: Formatters.currency(r.costPerPlant), color: AppTheme.infoBlue)),
              const SizedBox(width: 8),
              Expanded(child: _StatCard(label: 'Biaya/Ha', value: Formatters.currency(r.costPerHectare), color: AppTheme.accentOrange)),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(child: _StatCard(label: 'Estimasi Pendapatan', value: Formatters.currency(r.estimatedRevenue), color: AppTheme.primaryGreen)),
              const SizedBox(width: 8),
              Expanded(child: _StatCard(label: 'Estimasi Laba', value: Formatters.currency(r.profitEstimation), color: r.profitEstimation >= 0 ? AppTheme.primaryGreen : AppTheme.dangerRed)),
            ],
          ),
          const SizedBox(height: 8),
          _StatCard(label: 'ROI', value: Formatters.percentage(r.roiPercentage), color: AppTheme.accentOrange, fullWidth: true),
          const SizedBox(height: 16),
          Text('Rincian Biaya', style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          ...r.breakdown.map((b) => Card(
            margin: const EdgeInsets.only(bottom: 6),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              child: Row(
                children: [
                  Expanded(flex: 2, child: Text(b.category, style: const TextStyle(fontWeight: FontWeight.w500))),
                  Text(Formatters.currency(b.total), style: const TextStyle(fontWeight: FontWeight.bold)),
                  const SizedBox(width: 8),
                  SizedBox(
                    width: 40,
                    child: Text('${b.percentage.toStringAsFixed(1)}%', style: const TextStyle(fontSize: 12, color: Colors.grey)),
                  ),
                ],
              ),
            ),
          )),
          const SizedBox(height: 16),
          OutlinedButton(
            onPressed: () => notifier.calculate(),
            child: const Text('Hitung Ulang'),
          ),
        ],
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String label;
  final String value;
  final Color color;
  final bool fullWidth;

  const _StatCard({required this.label, required this.value, required this.color, this.fullWidth = false});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.only(bottom: fullWidth ? 0 : 0),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: const TextStyle(fontSize: 12, color: Colors.grey)),
            const SizedBox(height: 4),
            Text(value, style: TextStyle(fontSize: fullWidth ? 18 : 14, fontWeight: FontWeight.bold, color: color)),
          ],
        ),
      ),
    );
  }
}
