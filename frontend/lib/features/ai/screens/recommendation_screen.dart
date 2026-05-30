import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../data/models/ai_model.dart';
import '../../../data/repositories/ai_repository.dart';
import '../../farm/providers/farm_provider.dart';
import '../../../core/theme/app_theme.dart';
import '../../../data/models/farm_model.dart';

class RecommendationScreen extends ConsumerStatefulWidget {
  const RecommendationScreen({super.key});

  @override
  ConsumerState<RecommendationScreen> createState() => _RecommendationScreenState();
}

class _RecommendationScreenState extends ConsumerState<RecommendationScreen> {
  FarmModel? _selectedFarm;
  RecommendationListResponse? _recs;
  bool _loading = false;
  String _filter = 'all';

  @override
  void initState() {
    super.initState();
    Future.microtask(() => ref.invalidate(farmsProvider));
  }

  Future<void> _load() async {
    if (_selectedFarm == null) return;
    setState(() => _loading = true);
    try {
      final recs = await ref.read(aiRepositoryProvider).getRecommendations(_selectedFarm!.id);
      setState(() => _recs = recs);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
      }
    } finally {
      setState(() => _loading = false);
    }
  }

  List<RecommendationItem> get _filtered {
    if (_recs == null) return [];
    switch (_filter) {
      case 'urgent': return _recs!.urgent;
      case 'today': return _recs!.today;
      case 'week': return _recs!.thisWeek;
      default: return _recs!.all;
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final farmsAsync = ref.watch(farmsProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Rekomendasi AI')),
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            farmsAsync.when(
              loading: () => const CircularProgressIndicator(),
              error: (e, _) => Text('Error: $e'),
              data: (farms) => DropdownButtonFormField<int>(
                decoration: const InputDecoration(labelText: 'Pilih Lahan'),
                initialValue: _selectedFarm?.id,
                items: farms.map((f) => DropdownMenuItem(value: f.id, child: Text(f.name))).toList(),
                onChanged: (id) {
                  setState(() => _selectedFarm = farms.firstWhere((f) => f.id == id));
                  _load();
                },
              ),
            ),
            if (_recs != null) ...[
              const SizedBox(height: 16),
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: [
                    _buildFilterChip('Semua', 'all', _recs!.all.length),
                    _buildFilterChip('Mendesak', 'urgent', _recs!.urgent.length),
                    _buildFilterChip('Hari Ini', 'today', _recs!.today.length),
                    _buildFilterChip('Minggu Ini', 'week', _recs!.thisWeek.length),
                  ],
                ),
              ),
              const SizedBox(height: 12),
              if (_loading)
                const Center(child: CircularProgressIndicator())
              else if (_filtered.isEmpty)
                const Center(child: Padding(
                  padding: EdgeInsets.all(32),
                  child: Text('Tidak ada rekomendasi', style: TextStyle(color: Colors.grey)),
                ))
              else
                ..._filtered.map((r) => _buildRecommendationCard(theme, r)),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildFilterChip(String label, String value, int count) {
    final selected = _filter == value;
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: FilterChip(
        label: Text('$label ($count)'),
        selected: selected,
        onSelected: (_) => setState(() => _filter = value),
      ),
    );
  }

  Widget _buildRecommendationCard(ThemeData theme, RecommendationItem rec) {
    final color = rec.priority == 'high' ? AppTheme.dangerRed
        : rec.priority == 'medium' ? AppTheme.accentOrange : AppTheme.infoBlue;

    final icon = rec.type == 'fertilizer' ? Icons.science_outlined
        : rec.type == 'spray' ? Icons.water_drop
        : rec.type == 'irrigation' ? Icons.water
        : rec.type == 'harvest' ? Icons.calendar_month
        : Icons.lightbulb_outline;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, size: 20, color: color),
                const SizedBox(width: 8),
                Expanded(child: Text(rec.title, style: const TextStyle(fontWeight: FontWeight.bold))),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: color.withAlpha(30),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(rec.priority.toUpperCase(), style: TextStyle(fontSize: 10, color: color, fontWeight: FontWeight.bold)),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(rec.description, style: const TextStyle(fontSize: 13)),
            if (rec.timing != null) ...[
              const SizedBox(height: 4),
              Text('Waktu: ${rec.timing}', style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
            ],
            if (rec.dosage != null) ...[
              const SizedBox(height: 2),
              Text('Dosis: ${rec.dosage}', style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
            ],
            const SizedBox(height: 8),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.grey.shade50,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(rec.reasoning, style: TextStyle(fontSize: 11, color: Colors.grey.shade700, fontStyle: FontStyle.italic)),
            ),
          ],
        ),
      ),
    );
  }
}
