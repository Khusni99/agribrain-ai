import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../data/models/ai_model.dart';
import '../../../data/repositories/ai_repository.dart';
import '../../farm/providers/farm_provider.dart';
import '../../../core/theme/app_theme.dart';
import '../../../data/models/farm_model.dart';

class AIAdvisorScreen extends ConsumerStatefulWidget {
  const AIAdvisorScreen({super.key});

  @override
  ConsumerState<AIAdvisorScreen> createState() => _AIAdvisorScreenState();
}

class _AIAdvisorScreenState extends ConsumerState<AIAdvisorScreen> {
  final _queryController = TextEditingController();
  FarmModel? _selectedFarm;
  FieldModel? _selectedField;
  AIAdvisorResponse? _response;
  bool _loading = false;

  @override
  void dispose() {
    _queryController.dispose();
    super.dispose();
  }

  Future<void> _ask() async {
    if (_selectedFarm == null) return;
    setState(() => _loading = true);
    try {
      final resp = await ref.read(aiRepositoryProvider).getFarmAdvisor(
        _selectedFarm!.id,
        fieldId: _selectedField?.id,
        query: _queryController.text,
      );
      setState(() => _response = resp);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
      }
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final farmsAsync = ref.watch(farmsProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Tanya Agronomis AI')),
      body: RefreshIndicator(
        onRefresh: () async => ref.invalidate(farmsProvider),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              farmsAsync.when(
                loading: () => const CircularProgressIndicator(),
                error: (e, _) => Text('Gagal memuat lahan: $e'),
                data: (farms) => Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    DropdownButtonFormField<int>(
                      decoration: const InputDecoration(labelText: 'Pilih Lahan'),
                      initialValue: _selectedFarm?.id,
                      items: farms.map((f) => DropdownMenuItem(value: f.id, child: Text(f.name))).toList(),
                      onChanged: (id) {
                        setState(() {
                          _selectedFarm = farms.firstWhere((f) => f.id == id);
                          _selectedField = null;
                        });
                      },
                    ),
                    if (_selectedFarm != null) ...[
                      const SizedBox(height: 12),
                      Consumer(
                      builder: (_, ref, __) {
                        final fieldsAsync = ref.watch(farmFieldsProvider(_selectedFarm!.id));
                        return fieldsAsync.when(
                          loading: () => const SizedBox(),
                          error: (_, ___) => const SizedBox(),
                          data: (fields) => DropdownButtonFormField<int>(
                            decoration: const InputDecoration(labelText: 'Pilih Petak (opsional)'),
                            initialValue: _selectedField?.id,
                              items: [
                                const DropdownMenuItem(value: null, child: Text('Semua Petak')),
                                ...fields.map((f) => DropdownMenuItem(value: f.id, child: Text(f.name))),
                              ],
                              onChanged: (id) {
                                setState(() {
                                  _selectedField = id == null ? null : fields.firstWhere((f) => f.id == id);
                                });
                              },
                            ),
                          );
                        },
                      ),
                    ],
                  ],
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _queryController,
                maxLines: 3,
                decoration: const InputDecoration(
                  labelText: 'Pertanyaan Anda',
                  hintText: 'Contoh: Apa yang harus saya lakukan minggu ini?',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: (_selectedFarm != null && !_loading) ? _ask : null,
                  child: _loading
                      ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Text('Tanya AI'),
                ),
              ),
              if (_response != null) ...[
                const SizedBox(height: 24),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Saran AI', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                        const SizedBox(height: 8),
                        Text(_response!.advice),
                        if (_response!.fieldHealth != null) ...[
                          const SizedBox(height: 16),
                          _buildHealthCard(theme, _response!.fieldHealth!),
                        ],
                        if (_response!.recommendations != null && _response!.recommendations!.all.isNotEmpty) ...[
                          const SizedBox(height: 16),
                          Text('Rekomendasi', style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
                          const SizedBox(height: 8),
                          ..._response!.recommendations!.all.take(3).map((r) => _buildRecChip(r)),
                        ],
                      ],
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHealthCard(ThemeData theme, FieldHealthResponse health) {
    final color = health.healthScore >= 70 ? AppTheme.primaryGreen
        : health.healthScore >= 40 ? AppTheme.accentOrange : AppTheme.dangerRed;
    return Card(
      color: AppTheme.surfaceLight,
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            SizedBox(
              width: 60,
              height: 60,
              child: Stack(
                alignment: Alignment.center,
                children: [
                  CircularProgressIndicator(value: health.healthScore / 100, color: color, strokeWidth: 6),
                  Text('${health.healthScore.toInt()}', style: TextStyle(fontWeight: FontWeight.bold, color: color)),
                ],
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(health.fieldName, style: const TextStyle(fontWeight: FontWeight.bold)),
                  Text('Status: ${health.status}', style: TextStyle(color: Colors.grey.shade600, fontSize: 12)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecChip(RecommendationItem rec) {
    final color = rec.priority == 'high' ? AppTheme.dangerRed
        : rec.priority == 'medium' ? AppTheme.accentOrange : AppTheme.infoBlue;
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        children: [
          Icon(Icons.circle, size: 8, color: color),
          const SizedBox(width: 8),
          Expanded(child: Text(rec.title, style: const TextStyle(fontSize: 13))),
        ],
      ),
    );
  }
}
