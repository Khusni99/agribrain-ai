import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';

class WeatherCard extends StatelessWidget {
  final double temperature;
  final double humidity;
  final double rainfall;
  final String condition;
  final String? riskLevel;

  const WeatherCard({
    super.key,
    required this.temperature,
    required this.humidity,
    required this.rainfall,
    required this.condition,
    this.riskLevel,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.cloud, color: AppTheme.infoBlue),
                const SizedBox(width: 8),
                Text('Cuaca Hari Ini', style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                )),
                const Spacer(),
                Text(condition, style: theme.textTheme.bodySmall),
              ],
            ),
            const Divider(),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _WeatherItem(label: 'Suhu', value: '${temperature.toStringAsFixed(1)}°C', icon: Icons.thermostat, color: AppTheme.accentOrange),
                _WeatherItem(label: 'Kelembaban', value: '${humidity.toStringAsFixed(0)}%', icon: Icons.water_drop, color: AppTheme.infoBlue),
                _WeatherItem(label: 'Curah Hujan', value: '${rainfall.toStringAsFixed(1)} mm', icon: Icons.umbrella, color: AppTheme.dangerRed),
              ],
            ),
            if (riskLevel != null) ...[
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: riskLevel == 'TINGGI' ? AppTheme.dangerRed.withAlpha(25) : AppTheme.warningYellow.withAlpha(25),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(
                      riskLevel == 'TINGGI' ? Icons.warning_rounded : Icons.info_outline,
                      size: 16,
                      color: riskLevel == 'TINGGI' ? AppTheme.dangerRed : AppTheme.accentOrange,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Risiko Penyakit: $riskLevel',
                      style: TextStyle(
                        fontSize: 12,
                        color: riskLevel == 'TINGGI' ? AppTheme.dangerRed : AppTheme.accentOrange,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _WeatherItem extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color color;

  const _WeatherItem({required this.label, required this.value, required this.icon, required this.color});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon, color: color, size: 20),
        const SizedBox(height: 4),
        Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
        Text(label, style: const TextStyle(fontSize: 11, color: Colors.grey)),
      ],
    );
  }
}
