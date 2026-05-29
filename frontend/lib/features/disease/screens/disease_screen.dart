import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import '../providers/disease_provider.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/utils/formatters.dart';

class DiseaseScreen extends ConsumerWidget {
  const DiseaseScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(diseaseProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Deteksi Penyakit')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            if (state.imageFile == null) ...[
              Container(
                height: 200,
                decoration: BoxDecoration(
                  color: theme.colorScheme.surfaceContainerHighest.withAlpha(60),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: theme.colorScheme.outlineVariant, width: 2, strokeAlign: BorderSide.strokeAlignInside),
                ),
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.image_search, size: 64, color: theme.colorScheme.onSurfaceVariant.withAlpha(100)),
                      const SizedBox(height: 12),
                      Text('Upload foto tanaman', style: theme.textTheme.bodyLarge),
                      const SizedBox(height: 4),
                      Text('Ambil foto atau pilih dari galeri', style: theme.textTheme.bodySmall?.copyWith(color: Colors.grey)),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () => _pickImage(ref, ImageSource.camera),
                      icon: const Icon(Icons.camera_alt),
                      label: const Text('Kamera'),
                      style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primaryGreen, foregroundColor: Colors.white),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () => _pickImage(ref, ImageSource.gallery),
                      icon: const Icon(Icons.photo_library),
                      label: const Text('Galeri'),
                      style: ElevatedButton.styleFrom(backgroundColor: AppTheme.infoBlue, foregroundColor: Colors.white),
                    ),
                  ),
                ],
              ),
            ] else ...[
              ClipRRect(
                borderRadius: BorderRadius.circular(16),
                child: Image.file(state.imageFile!, height: 250, width: double.infinity, fit: BoxFit.cover),
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
                      onPressed: state.isLoading ? null : () => ref.read(diseaseProvider.notifier).detect(),
                      icon: state.isLoading
                          ? const SizedBox(height: 18, width: 18, child: CircularProgressIndicator(strokeWidth: 2))
                          : const Icon(Icons.search),
                      label: Text(state.isLoading ? 'Memeriksa...' : 'Deteksi'),
                      style: ElevatedButton.styleFrom(backgroundColor: AppTheme.dangerRed, foregroundColor: Colors.white),
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
                  child: Text(state.error!, style: const TextStyle(color: AppTheme.dangerRed)),
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

  Future<void> _pickImage(WidgetRef ref, ImageSource source) async {
    final picker = ImagePicker();
    final xFile = await picker.pickImage(source: source, maxWidth: 1024, maxHeight: 1024);
    if (xFile != null) {
      ref.read(diseaseProvider.notifier).setImage(File(xFile.path));
    }
  }
}

class _ResultCard extends StatelessWidget {
  final dynamic result;
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
                Text('Hasil Deteksi', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
              ],
            ),
            const Divider(),
            _Row(label: 'Penyakit', value: result.diseaseName),
            _Row(label: 'Tingkat Keparahan', value: '${result.severityPercentage.toStringAsFixed(1)}%'),
            _Row(label: 'Keyakinan', value: '${(result.confidenceScore * 100).toStringAsFixed(0)}%'),
            if (result.economicImpact != null) ...[
              const Divider(),
              Text('Dampak Ekonomi', style: theme.textTheme.labelLarge?.copyWith(fontWeight: FontWeight.bold)),
              _Row(label: 'Kehilangan Hasil', value: '${result.economicImpact.estimatedYieldLossPercent.toStringAsFixed(1)}%'),
              _Row(label: 'Kerugian per Ha', value: Formatters.currency(result.economicImpact.estimatedRevenueLossPerHectare)),
            ],
            const Divider(),
            Text('Rekomendasi Penanganan', style: theme.textTheme.labelLarge?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            ...result.treatmentRecommendations.map((t) => Padding(
              padding: const EdgeInsets.only(bottom: 6),
              child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const Text('• ', style: TextStyle(fontWeight: FontWeight.bold)),
                Expanded(child: Text(t)),
              ]),
            )),
          ],
        ),
      ),
    );
  }
}

class _Row extends StatelessWidget {
  final String label;
  final String value;
  const _Row({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}
