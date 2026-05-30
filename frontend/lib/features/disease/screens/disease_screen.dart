import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import '../providers/disease_provider.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/utils/formatters.dart';
import '../../../data/models/disease_model.dart';

class DiseaseScreen extends ConsumerWidget {
  const DiseaseScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(diseaseProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Deteksi Penyakit'),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            tooltip: 'Riwayat Deteksi',
            onPressed: () => context.push('/disease/history'),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            if (state.imageFile == null) ...[
              _buildUploadPrompt(theme, ref),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () => _pickImage(ref, ImageSource.camera),
                      icon: const Icon(Icons.camera_alt),
                      label: const Text('Kamera'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.primaryGreen,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () => _pickImage(ref, ImageSource.gallery),
                      icon: const Icon(Icons.photo_library),
                      label: const Text('Galeri'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.infoBlue,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),
                ],
              ),
            ] else ...[
              ClipRRect(
                borderRadius: BorderRadius.circular(16),
                child: Image.file(
                  state.imageFile!,
                  height: 250,
                  width: double.infinity,
                  fit: BoxFit.cover,
                ),
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => ref.read(diseaseProvider.notifier).reset(),
                      icon: const Icon(Icons.refresh),
                      label: const Text('Ganti Foto'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: state.isLoading
                          ? null
                          : () => ref.read(diseaseProvider.notifier).detect(),
                      icon: state.isLoading
                          ? const SizedBox(
                              height: 18,
                              width: 18,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.search),
                      label: Text(state.isLoading ? 'Memeriksa...' : 'Deteksi'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.dangerRed,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),
                ],
              ),
            ],
            const SizedBox(height: 16),
            if (state.error != null)
              Card(
                color: AppTheme.dangerRed.withAlpha(20),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text(
                    state.error!,
                    style: const TextStyle(color: AppTheme.dangerRed),
                  ),
                ),
              ),
            if (state.result != null) ...[
              _ResultCard(result: state.result!, theme: theme),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildUploadPrompt(ThemeData theme, WidgetRef ref) {
    return Container(
      height: 200,
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest.withAlpha(60),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: theme.colorScheme.outlineVariant,
          width: 2,
          strokeAlign: BorderSide.strokeAlignInside,
        ),
      ),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.image_search,
              size: 64,
              color: theme.colorScheme.onSurfaceVariant.withAlpha(100),
            ),
            const SizedBox(height: 12),
            Text('Upload foto tanaman', style: theme.textTheme.bodyLarge),
            const SizedBox(height: 4),
            Text(
              'Ambil foto atau pilih dari galeri',
              style: theme.textTheme.bodySmall
                  ?.copyWith(color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _pickImage(WidgetRef ref, ImageSource source) async {
    final picker = ImagePicker();
    final xFile = await picker.pickImage(
      source: source,
      maxWidth: 1024,
      maxHeight: 1024,
    );
    if (xFile != null) {
      ref.read(diseaseProvider.notifier).setImage(File(xFile.path));
    }
  }
}

class _SeverityIndicator extends StatelessWidget {
  final double severity;
  final double confidence;

  const _SeverityIndicator({
    required this.severity,
    required this.confidence,
  });

  Color get _severityColor {
    if (severity < 30) return AppTheme.primaryGreen;
    if (severity < 60) return AppTheme.accentOrange;
    return AppTheme.dangerRed;
  }

  String get _severityLabel {
    if (severity < 30) return 'RENDAH';
    if (severity < 60) return 'SEDANG';
    return 'TINGGI';
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        SizedBox(
          height: 100,
          width: 100,
          child: Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                height: 100,
                width: 100,
                child: CircularProgressIndicator(
                  value: severity / 100,
                  strokeWidth: 8,
                  backgroundColor: Colors.grey.shade200,
                  valueColor: AlwaysStoppedAnimation<Color>(_severityColor),
                ),
              ),
              Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    '${severity.toStringAsFixed(0)}%',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: _severityColor,
                    ),
                  ),
                  Text(
                    _severityLabel,
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      color: _severityColor,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 8),
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.verified, size: 14, color: Colors.grey),
            const SizedBox(width: 4),
            Text(
              'Keyakinan: ${(confidence * 100).toStringAsFixed(0)}%',
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
        ),
      ],
    );
  }
}

class _BoundingBoxSummary extends StatelessWidget {
  final List<BoundingBox> boxes;

  const _BoundingBoxSummary({required this.boxes});

  @override
  Widget build(BuildContext context) {
    if (boxes.isEmpty) return const SizedBox.shrink();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Area Terdeteksi',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
        const SizedBox(height: 4),
        ...boxes.map((b) => Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Row(
                children: [
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: AppTheme.dangerRed.withAlpha(20),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      b.label,
                      style: const TextStyle(fontSize: 11),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    '${(b.confidence * 100).toStringAsFixed(0)}%',
                    style: const TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                ],
              ),
            )),
      ],
    );
  }
}

class _ResultCard extends StatelessWidget {
  final DiseaseModel result;
  final ThemeData theme;

  const _ResultCard({required this.result, required this.theme});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.healing, color: AppTheme.dangerRed),
                const SizedBox(width: 8),
                Text(
                  'Hasil Deteksi',
                  style: theme.textTheme.titleMedium
                      ?.copyWith(fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const Divider(),
            Center(
              child: _SeverityIndicator(
                severity: result.severity,
                confidence: result.confidence,
              ),
            ),
            const SizedBox(height: 16),
            _InfoRow(
              label: 'Penyakit',
              value: result.diseaseName,
              valueStyle: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
                color: AppTheme.dangerRed,
              ),
            ),
            const SizedBox(height: 4),
            _InfoRow(
              label: 'Provider',
              value: result.detectionProvider ?? '-',
            ),
            const SizedBox(height: 12),
            if (result.boundingBoxes.isNotEmpty) ...[
              _BoundingBoxSummary(boxes: result.boundingBoxes),
              const Divider(),
            ],
            Text(
              'Rekomendasi Penanganan',
              style: theme.textTheme.labelLarge
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            ...result.recommendations.map(
              (t) => Padding(
                padding: const EdgeInsets.only(bottom: 6),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.check_circle_outline,
                        size: 16, color: AppTheme.primaryGreen),
                    const SizedBox(width: 8),
                    Expanded(child: Text(t, style: const TextStyle(fontSize: 13))),
                  ],
                ),
              ),
            ),
            if (result.prevention.isNotEmpty) ...[
              const Divider(),
              Text(
                'Pencegahan',
                style: theme.textTheme.labelLarge
                    ?.copyWith(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              ...result.prevention.map(
                (p) => Padding(
                  padding: const EdgeInsets.only(bottom: 6),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Icon(Icons.shield_outlined,
                          size: 16, color: AppTheme.infoBlue),
                      const SizedBox(width: 8),
                      Expanded(child: Text(p, style: const TextStyle(fontSize: 13))),
                    ],
                  ),
                ),
              ),
            ],
            const Divider(),
            Text(
              'Dampak Ekonomi',
              style: theme.textTheme.labelLarge
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            _InfoRow(
              label: 'Kehilangan Hasil',
              value: '${result.economicRisk.estimatedYieldLossPercent.toStringAsFixed(1)}%',
            ),
            _InfoRow(
              label: 'Kerugian per Ha',
              value: Formatters.currency(
                  result.economicRisk.estimatedRevenueLossPerHectare),
            ),
            _InfoRow(
              label: 'Tingkat Risiko',
              value: result.economicRisk.riskLevel,
              valueStyle: TextStyle(
                fontWeight: FontWeight.bold,
                color: result.economicRisk.riskLevel == 'TINGGI'
                    ? AppTheme.dangerRed
                    : result.economicRisk.riskLevel == 'SEDANG'
                        ? AppTheme.accentOrange
                        : AppTheme.primaryGreen,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;
  final TextStyle? valueStyle;

  const _InfoRow({
    required this.label,
    required this.value,
    this.valueStyle,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey, fontSize: 13)),
          Text(
            value,
            style: valueStyle ??
                const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
          ),
        ],
      ),
    );
  }
}
