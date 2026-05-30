import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class BrandHeader extends StatelessWidget {
  final bool showTagline;

  const BrandHeader({super.key, this.showTagline = true});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 80,
          height: 80,
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [AppTheme.primaryGreen, AppTheme.secondaryGreen],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(20),
            boxShadow: [
              BoxShadow(
                color: AppTheme.primaryGreen.withAlpha(60),
                blurRadius: 16,
                offset: const Offset(0, 6),
              ),
            ],
          ),
          child: const Icon(
            Icons.agriculture_rounded,
            size: 44,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 16),
        Text(
          'AgriBrain AI',
          style: theme.textTheme.headlineMedium?.copyWith(
            fontWeight: FontWeight.w800,
            color: AppTheme.primaryGreen,
            letterSpacing: -0.5,
          ),
        ),
        if (showTagline) ...[
          const SizedBox(height: 6),
          Text(
            'Asisten Cerdas Petani Modern',
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ],
    );
  }
}
