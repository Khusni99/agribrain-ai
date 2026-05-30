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
import '../../../core/widgets/status_badge.dart';
import '../../farm/screens/farm_list_screen.dart';

class RecommendationScreen extends ConsumerStatefulWidget {
  const RecommendationScreen({super.key});

  @override
  ConsumerState<RecommendationScreen> createState() => _RecommendationScreenState();
}

class _RecommendationScreenState extends ConsumerState<RecommendationScreen> {
  int? _selectedFarmId;
  RecommendationListResponse? _recs;
  bool _loading = false;
  String _filter = 'all';

  @override
  void initState() {
    super.initState();
    Future.microtask(() => ref.invalidate(farmsProvider));
  }

  Future<void> _load() async {
    if (_selectedFarmId == null) return;
    setState(() => _loading = true);
    try {
      final recs = await ref.read(aiRepositoryProvider).getRecommendations(_selectedFarmId!);
      setState(() => _recs = recs);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Gagal: $e')));
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
              loading: () => const LoadingView(message: 'Memuat lahan...'),
              error: (e, _) => ErrorView(message: 'Error: $e', onRetry: () => ref.invalidate(farmsProvider)),
              data: (farms) {
                if (farms.isEmpty) {
                  return Column(
                    children: [
                      EmptyState(
                        icon: Icons.agriculture,
                        title: 'Belum ada lahan',
                        subtitle: 'Tambahkan lahan untuk mendapat rekomendasi',
                      ),
                      TextButton(
                        onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const FarmListScreen())),
                        child: const Text('Tambah Lahan'),
                      ),
                    ],
                  );
                }
                return DropdownButtonFormField<int>(
                  decoration: const InputDecoration(
                    labelText: 'Pilih Lahan',
                    prefixIcon: Icon(Icons.terrain),
                  ),
                  value: _selectedFarmId,
                  hint: const Text('Pilih lahan...'),
                  items: farms.map((f) => DropdownMenuItem(value: f.id, child: Text(f.name))).toList(),
                  onChanged: (id) {
                    setState(() {
                      _selectedFarmId = id;
                    });
                    _load();
                  },
                );
              },
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
                const LoadingView(message: 'Memuat rekomendasi...')
              else if (_filtered.isEmpty)
                const EmptyState(
                  icon: Icons.check_circle_outline,
                  title: 'Tidak ada rekomendasi',
                  subtitle: 'Semua jadwal sudah sesuai',
                )
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
    final color = rec.priority == 'high'
        ? AppTheme.dangerRed
        : rec.priority == 'medium'
            ? AppTheme.accentOrange
            : AppTheme.infoBlue;

    final icon = rec.type == 'fertilizer' ? Icons.science_outlined
        : rec.type == 'spray' ? Icons.water_drop
        : rec.type == 'irrigation' ? Icons.water
        : rec.type == 'harvest' ? Icons.calendar_month
        : Icons.lightbulb_outline;

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: AgriCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: color.withAlpha(25),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(icon, size: 20, color: color),
              ),
              const SizedBox(width: 12),
              Expanded(child: Text(rec.title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15))),
              StatusBadge.priority(rec.priority),
            ],
          ),
          const SizedBox(height: 12),
          Text(rec.description, style: const TextStyle(fontSize: 13, height: 1.4)),
          if (rec.timing != null) ...[
            const SizedBox(height: 6),
            Row(
              children: [
                Icon(Icons.schedule, size: 14, color: Colors.grey.shade600),
                const SizedBox(width: 4),
                Text('Waktu: ${rec.timing}', style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
              ],
            ),
          ],
          if (rec.dosage != null) ...[
            const SizedBox(height: 2),
            Row(
              children: [
                Icon(Icons.science, size: 14, color: Colors.grey.shade600),
                const SizedBox(width: 4),
                Text('Dosis: ${rec.dosage}', style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
              ],
            ),
          ],
          const SizedBox(height: 8),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: Colors.grey.shade50,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.grey.shade200),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(Icons.lightbulb_outline, size: 14, color: AppTheme.accentOrange),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(rec.reasoning, style: TextStyle(fontSize: 11, color: Colors.grey.shade700, fontStyle: FontStyle.italic, height: 1.4)),
                ),
              ],
            ),
          ),
        ],
      ),
      ),
    );
  }
}
