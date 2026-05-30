import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../data/repositories/ai_repository.dart';
import '../../../data/models/ai_model.dart';
final aiAdvisorProvider =
    FutureProvider.family<AIAdvisorResponse, int>((ref, farmId) async {
  return ref.read(aiRepositoryProvider).getFarmAdvisor(farmId);
});

final aiRecommendationsProvider =
    FutureProvider.family<RecommendationListResponse, int>((ref, farmId) async {
  return ref.read(aiRepositoryProvider).getRecommendations(farmId);
});

final aiFieldHealthProvider =
    FutureProvider.family<FieldHealthResponse, int>((ref, fieldId) async {
  return ref.read(aiRepositoryProvider).getFieldHealth(fieldId);
});
