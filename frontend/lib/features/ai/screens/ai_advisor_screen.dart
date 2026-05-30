import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../data/models/ai_model.dart';
import '../../../data/repositories/ai_repository.dart';
import '../../farm/providers/farm_provider.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/widgets/agri_card.dart';
import '../../../core/widgets/loading_view.dart';
import '../../../core/widgets/error_view.dart';
import '../../../core/widgets/empty_state.dart';
import '../../farm/screens/farm_list_screen.dart';

class AIAdvisorScreen extends ConsumerStatefulWidget {
  const AIAdvisorScreen({super.key});

  @override
  ConsumerState<AIAdvisorScreen> createState() => _AIAdvisorScreenState();
}

class _AIAdvisorScreenState extends ConsumerState<AIAdvisorScreen> {
  final _queryController = TextEditingController();
  final _scrollController = ScrollController();
  int? _selectedFarmId;
  int? _selectedFieldId;
  AIAdvisorResponse? _response;
  bool _loading = false;

  @override
  void dispose() {
    _queryController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _ask() async {
    if (_selectedFarmId == null) return;
    setState(() => _loading = true);
    try {
      final resp = await ref.read(aiRepositoryProvider).getFarmAdvisor(
        _selectedFarmId!,
        fieldId: _selectedFieldId,
        query: _queryController.text,
      );
      setState(() => _response = resp);
      Future.delayed(const Duration(milliseconds: 300), () {
        if (_scrollController.hasClients) {
          _scrollController.animateTo(
            _scrollController.position.maxScrollExtent,
            duration: const Duration(milliseconds: 400),
            curve: Curves.easeOut,
          );
        }
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Gagal: $e')),
        );
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
          controller: _scrollController,
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              farmsAsync.when(
                loading: () => const LoadingView(message: 'Memuat data lahan...'),
                error: (e, _) => ErrorView(
                  message: 'Gagal memuat lahan: $e',
                  onRetry: () => ref.invalidate(farmsProvider),
                ),
                data: (farms) {
                  if (farms.isEmpty) {
                    return Column(
                      children: [
                        EmptyState(
                          icon: Icons.agriculture,
                          title: 'Belum ada lahan',
                          subtitle: 'Tambahkan lahan terlebih dahulu untuk bertanya pada AI',
                        ),
                        TextButton(
                          onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const FarmListScreen())),
                          child: const Text('Tambah Lahan'),
                        ),
                      ],
                    );
                  }
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      DropdownButtonFormField<int>(
                        decoration: const InputDecoration(
                          labelText: 'Pilih Lahan',
                          prefixIcon: Icon(Icons.terrain),
                        ),
                        value: _selectedFarmId,
                        hint: const Text('Pilih lahan...'),
                        items: farms.map((f) => DropdownMenuItem(
                          value: f.id,
                          child: Text(f.name),
                        )).toList(),
                        onChanged: (id) {
                          setState(() {
                            _selectedFarmId = id;
                            _selectedFieldId = null;
                          });
                        },
                      ),
                      if (_selectedFarmId != null) ...[
                        const SizedBox(height: 12),
                        Consumer(
                          builder: (_, ref, __) {
                            final fieldsAsync = ref.watch(farmFieldsProvider(_selectedFarmId!));
                            return fieldsAsync.when(
                              loading: () => const SizedBox(),
                              error: (_, ___) => const SizedBox(),
                              data: (fields) => DropdownButtonFormField<int>(
                                decoration: const InputDecoration(
                                  labelText: 'Pilih Petak (opsional)',
                                  prefixIcon: Icon(Icons.grid_view),
                                ),
                                value: _selectedFieldId,
                                hint: const Text('Semua Petak'),
                                items: [
                                  const DropdownMenuItem(value: null, child: Text('Semua Petak')),
                                  ...fields.map((f) => DropdownMenuItem(value: f.id, child: Text(f.name))),
                                ],
                                onChanged: (id) {
                                  setState(() {
                                    _selectedFieldId = id;
                                    _selectedFieldId = id;
                                  });
                                },
                              ),
                            );
                          },
                        ),
                      ],
                    ],
                  );
                },
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _queryController,
                maxLines: 3,
                decoration: const InputDecoration(
                  labelText: 'Pertanyaan Anda',
                  hintText: 'Contoh: Apa yang harus saya lakukan minggu ini?',
                  prefixIcon: Padding(
                    padding: EdgeInsets.only(bottom: 48),
                    child: Icon(Icons.help_outline),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: FilledButton.icon(
                  onPressed: (_selectedFarmId != null && !_loading) ? _ask : null,
                  icon: _loading
                      ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                      : const Icon(Icons.send_rounded),
                  label: const Text('Tanya AI'),
                ),
              ),
              if (_response != null) ...[
                const SizedBox(height: 24),
                AgriCard(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: AppTheme.primaryGreen.withAlpha(25),
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: const Icon(Icons.psychology, color: AppTheme.primaryGreen, size: 24),
                          ),
                          const SizedBox(width: 12),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Saran AI', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                            ],
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      Text(_response!.advice, style: const TextStyle(fontSize: 14, height: 1.5)),
                      if (_response!.fieldHealth != null) ...[
                        const SizedBox(height: 16),
                        _buildHealthCard(_response!.fieldHealth!),
                      ],
                      if (_response!.recommendations != null && _response!.recommendations!.all.isNotEmpty) ...[
                        const SizedBox(height: 16),
                        Text('Rekomendasi', style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
                        const SizedBox(height: 8),
                        ..._response!.recommendations!.all.take(3).map(_buildRecChip),
                      ],
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHealthCard(FieldHealthResponse health) {
    final color = health.healthScore >= 70
        ? AppTheme.primaryGreen
        : health.healthScore >= 40
            ? AppTheme.accentOrange
            : AppTheme.dangerRed;
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withAlpha(12),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withAlpha(50)),
      ),
      child: Row(
        children: [
          SizedBox(
            width: 60, height: 60,
            child: Stack(
              alignment: Alignment.center,
              children: [
                CircularProgressIndicator(
                  value: health.healthScore / 100,
                  color: color,
                  strokeWidth: 6,
                  backgroundColor: Colors.grey.shade200,
                ),
                Text('${health.healthScore.toInt()}', style: TextStyle(fontWeight: FontWeight.bold, color: color, fontSize: 16)),
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
    );
  }

  Widget _buildRecChip(RecommendationItem rec) {
    final color = rec.priority == 'high'
        ? AppTheme.dangerRed
        : rec.priority == 'medium'
            ? AppTheme.accentOrange
            : AppTheme.infoBlue;
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
