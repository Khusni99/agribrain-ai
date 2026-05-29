import 'package:flutter/material.dart';
import '../providers/chat_provider.dart';
import '../../../core/theme/app_theme.dart';

class ChatBubble extends StatelessWidget {
  final ChatMessage message;

  const ChatBubble({super.key, required this.message});

  @override
  Widget build(BuildContext context) {
    if (message.isUser) return _userBubble(context);
    return _aiBubble(context);
  }

  Widget _userBubble(BuildContext context) {
    return Align(
      alignment: Alignment.centerRight,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12, left: 50),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          color: AppTheme.primaryGreen,
          borderRadius: BorderRadius.circular(16).copyWith(bottomRight: Radius.zero),
        ),
        child: Text(message.text, style: const TextStyle(color: Colors.white)),
      ),
    );
  }

  Widget _aiBubble(BuildContext context) {
    final d = message.diagnosis;
    final theme = Theme.of(context);

    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12, right: 50),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          color: theme.colorScheme.surfaceContainerHighest.withAlpha(100),
          borderRadius: BorderRadius.circular(16).copyWith(bottomLeft: Radius.zero),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(message.text, style: theme.textTheme.bodyMedium),
            if (d != null) ...[
              const SizedBox(height: 8),
              if (d.possibleCauses.isNotEmpty) ...[
                const Divider(),
                Text('Penyebab', style: theme.textTheme.labelLarge?.copyWith(fontWeight: FontWeight.bold, color: AppTheme.dangerRed)),
                const SizedBox(height: 4),
                ...d.possibleCauses.map((c) => Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('• ', style: TextStyle(fontWeight: FontWeight.bold)),
                      Expanded(
                        child: RichText(
                          text: TextSpan(
                            style: theme.textTheme.bodySmall,
                            children: [
                              TextSpan(text: c.cause, style: const TextStyle(fontWeight: FontWeight.bold)),
                              TextSpan(text: ' (${c.confidence.toStringAsFixed(0)}%)'),
                              TextSpan(text: '\n${c.action}', style: const TextStyle(color: Colors.grey)),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                )),
              ],
              if (d.recommendedActions.isNotEmpty) ...[
                const SizedBox(height: 8),
                const Divider(),
                Text('Tindakan', style: theme.textTheme.labelLarge?.copyWith(fontWeight: FontWeight.bold, color: AppTheme.primaryGreen)),
                const SizedBox(height: 4),
                ...d.recommendedActions.map((a) => Padding(
                  padding: const EdgeInsets.only(bottom: 2),
                  child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    const Text('✓ ', style: TextStyle(color: AppTheme.primaryGreen)),
                    Expanded(child: Text(a, style: theme.textTheme.bodySmall)),
                  ]),
                )),
              ],
              if (d.fertilizerRecommendations != null && d.fertilizerRecommendations!.isNotEmpty) ...[
                const SizedBox(height: 8),
                const Divider(),
                Text('Rekomendasi Pupuk', style: theme.textTheme.labelLarge?.copyWith(fontWeight: FontWeight.bold, color: AppTheme.accentOrange)),
                ...d.fertilizerRecommendations!.map((f) => Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: Text('• ${f.type}: ${f.dosage} (${f.timing})', style: theme.textTheme.bodySmall),
                )),
              ],
              if (d.confidenceScore > 0) ...[
                const SizedBox(height: 8),
                Row(
                  children: [
                    const Icon(Icons.verified, size: 14, color: AppTheme.primaryGreen),
                    const SizedBox(width: 4),
                    Text('Kepercayaan: ${(d.confidenceScore * 100).toStringAsFixed(0)}%',
                        style: const TextStyle(fontSize: 11, color: Colors.grey)),
                  ],
                ),
              ],
            ],
          ],
        ),
      ),
    );
  }
}
