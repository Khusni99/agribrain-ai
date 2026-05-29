import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';
import '../../../data/models/market_price_model.dart';

class MarketPricePreview extends StatelessWidget {
  final List<MarketPriceModel> prices;

  const MarketPricePreview({super.key, required this.prices});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final displayPrices = prices.take(4).toList();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.trending_up, color: AppTheme.primaryGreen),
                const SizedBox(width: 8),
                Text('Harga Pasar', style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                )),
                const Spacer(),
                TextButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.open_in_new, size: 16),
                  label: const Text('Lihat Semua', style: TextStyle(fontSize: 12)),
                ),
              ],
            ),
            const Divider(),
            ...displayPrices.map((p) => Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: Row(
                children: [
                  Expanded(flex: 2, child: Text(p.commodity, style: const TextStyle(fontWeight: FontWeight.w500))),
                  Expanded(
                    child: Text(
                      'Rp ${p.avgPrice?.toStringAsFixed(0) ?? '-'}',
                      textAlign: TextAlign.right,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
                  SizedBox(
                    width: 60,
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        Icon(
                          p.trend == 'naik' ? Icons.arrow_upward : p.trend == 'turun' ? Icons.arrow_downward : Icons.remove,
                          size: 14,
                          color: p.trend == 'naik' ? AppTheme.primaryGreen : p.trend == 'turun' ? AppTheme.dangerRed : Colors.grey,
                        ),
                        const SizedBox(width: 2),
                        Text(
                          p.trend ?? '-',
                          style: TextStyle(fontSize: 11, color: p.trend == 'naik' ? AppTheme.primaryGreen : p.trend == 'turun' ? AppTheme.dangerRed : Colors.grey),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            )),
          ],
        ),
      ),
    );
  }
}
