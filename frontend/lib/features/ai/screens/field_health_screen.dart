import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/ai_provider.dart';
import '../../../data/models/ai_model.dart';
import '../../../core/theme/app_theme.dart';

class FieldHealthScreen extends ConsumerWidget {
  final int fieldId;
  final String fieldName;

  const FieldHealthScreen({
    super.key,
    required this.fieldId,
    required this.fieldName,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final healthAsync = ref.watch(aiFieldHealthProvider(fieldId));

    return Scaffold(
      appBar: AppBar(title: Text('Kesehatan $fieldName')),
      body: healthAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (health) => RefreshIndicator(
          onRefresh: () async => ref.invalidate(aiFieldHealthProvider(fieldId)),
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildHealthScoreCard(theme, health),
                const SizedBox(height: 16),
                Text('Faktor Kesehatan', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                ...health.factors.map((f) => _buildFactorTile(f)),
                const SizedBox(height: 16),
                Text('Resiko Penyakit', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                _buildRiskCard(theme, health.diseaseRisk, AppTheme.dangerRed),
                const SizedBox(height: 16),
                Text('Resiko Nutrisi', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                _buildRiskCard(theme, health.nutrientRisk, AppTheme.accentOrange),
                const SizedBox(height: 16),
                Text('Prakiraan Panen', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      children: [
                        _buildForecastRow('Prediksi Hasil', '${health.yieldForecast.predictedYieldKg.toStringAsFixed(0)} kg'),
                        _buildForecastRow('Per Hektar', '${health.yieldForecast.predictedYieldPerHectare.toStringAsFixed(0)} kg/ha'),
                        _buildForecastRow('Estimasi Pendapatan', 'Rp ${health.yieldForecast.predictedRevenue.toStringAsFixed(0)}'),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHealthScoreCard(ThemeData theme, FieldHealthResponse health) {
    final color = health.healthScore >= 70 ? AppTheme.primaryGreen
        : health.healthScore >= 40 ? AppTheme.accentOrange : AppTheme.dangerRed;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            SizedBox(
              width: 100,
              height: 100,
              child: Stack(
                alignment: Alignment.center,
                children: [
                  CircularProgressIndicator(value: health.healthScore / 100, color: color, strokeWidth: 10),
                  Text('${health.healthScore.toInt()}', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: color)),
                ],
              ),
            ),
            const SizedBox(height: 12),
            Text(health.fieldName, style: theme.textTheme.titleLarge),
            Text('Status: ${health.status}', style: TextStyle(color: Colors.grey.shade600)),
          ],
        ),
      ),
    );
  }

  Widget _buildFactorTile(HealthFactor factor) {
    final color = factor.severity == 'high' ? AppTheme.dangerRed
        : factor.severity == 'medium' ? AppTheme.accentOrange : AppTheme.primaryGreen;
    return ListTile(
      dense: true,
      leading: Icon(Icons.circle, size: 12, color: color),
      title: Text(factor.factor, style: const TextStyle(fontSize: 13)),
      subtitle: Text(factor.impact, style: const TextStyle(fontSize: 11)),
    );
  }

  Widget _buildRiskCard(ThemeData theme, RiskFactor risk, Color color) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(risk.description, style: const TextStyle(fontWeight: FontWeight.bold)),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(color: color.withAlpha(30), borderRadius: BorderRadius.circular(12)),
                  child: Text(risk.level, style: TextStyle(fontSize: 11, color: color, fontWeight: FontWeight.bold)),
                ),
              ],
            ),
            if (risk.contributingFactors.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text('Faktor:', style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
              ...risk.contributingFactors.map((f) => Text('  • $f', style: const TextStyle(fontSize: 12))),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildForecastRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(color: Colors.grey.shade600)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}
