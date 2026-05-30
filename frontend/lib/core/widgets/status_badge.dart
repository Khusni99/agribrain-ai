import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class StatusBadge extends StatelessWidget {
  final String label;
  final Color? color;
  final double fontSize;

  const StatusBadge({
    super.key,
    required this.label,
    this.color,
    this.fontSize = 11,
  });

  factory StatusBadge.risk(String level) {
    final color = level == 'TINGGI'
        ? AppTheme.dangerRed
        : level == 'SEDANG'
            ? AppTheme.accentOrange
            : AppTheme.primaryGreen;
    return StatusBadge(label: level, color: color);
  }

  factory StatusBadge.priority(String level) {
    final color = level == 'high'
        ? AppTheme.dangerRed
        : level == 'medium'
            ? AppTheme.accentOrange
            : AppTheme.infoBlue;
    return StatusBadge(label: level.toUpperCase(), color: color);
  }

  @override
  Widget build(BuildContext context) {
    final bgColor = color ?? AppTheme.primaryGreen;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: bgColor.withAlpha(25),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: fontSize,
          fontWeight: FontWeight.w700,
          color: bgColor,
        ),
      ),
    );
  }
}
