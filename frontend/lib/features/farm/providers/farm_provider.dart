import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../data/repositories/farm_repository.dart';
import '../../../data/models/farm_model.dart';

final farmsProvider =
    StateNotifierProvider<FarmListNotifier, AsyncValue<List<FarmModel>>>((ref) {
  return FarmListNotifier(ref.read(farmRepositoryProvider));
});

final farmDetailProvider =
    FutureProvider.family<FarmModel, int>((ref, id) async {
  return ref.read(farmRepositoryProvider).getFarm(id);
});

final farmFieldsProvider =
    FutureProvider.family<List<FieldModel>, int>((ref, farmId) async {
  return ref.read(farmRepositoryProvider).getFields(farmId);
});

final farmDashboardProvider =
    FutureProvider.family<DashboardSummaryModel, int>((ref, farmId) async {
  return ref.read(farmRepositoryProvider).getDashboard(farmId);
});

final farmTimelineProvider =
    FutureProvider.family<List<ActivityModel>, int>((ref, farmId) async {
  return ref.read(farmRepositoryProvider).getTimeline(farmId);
});

final farmRemindersProvider =
    FutureProvider.family<List<UpcomingTaskModel>, int>((ref, farmId) async {
  return ref.read(farmRepositoryProvider).getReminders(farmId);
});

class FarmListNotifier extends StateNotifier<AsyncValue<List<FarmModel>>> {
  final FarmRepository _repo;

  FarmListNotifier(this._repo) : super(const AsyncValue.loading()) {
    load();
  }

  Future<void> load() async {
    state = const AsyncValue.loading();
    try {
      final farms = await _repo.getFarms();
      state = AsyncValue.data(farms);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<FarmModel> create(Map<String, dynamic> data) async {
    final farm = await _repo.createFarm(data);
    await load();
    return farm;
  }

  Future<FarmModel> update(int id, Map<String, dynamic> data) async {
    final farm = await _repo.updateFarm(id, data);
    await load();
    return farm;
  }

  Future<void> delete(int id) async {
    await _repo.deleteFarm(id);
    await load();
  }

  Future<FieldModel> createField(int farmId, Map<String, dynamic> data) async {
    final field = await _repo.createField(farmId, data);
    return field;
  }
}
