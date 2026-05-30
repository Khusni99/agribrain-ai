import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/ai_model.dart';
import '../../core/network/api_client.dart';

final aiRepositoryProvider = Provider<AIRepository>((ref) {
  return AIRepository(ref.read(apiClientProvider));
});

class AIRepository {
  final ApiClient _client;

  AIRepository(this._client);

  Future<AIAdvisorResponse> getFarmAdvisor(int farmId, {int? fieldId, String query = ''}) async {
    final response = await _client.post('/ai/farm-advisor', data: {
      'farm_id': farmId,
      if (fieldId != null) 'field_id': fieldId,
      'query': query,
    });
    return AIAdvisorResponse.fromJson(response.data);
  }

  Future<RecommendationListResponse> getRecommendations(int farmId, {int? fieldId, List<String>? types}) async {
    final response = await _client.post('/ai/recommendations', data: {
      'farm_id': farmId,
      if (fieldId != null) 'field_id': fieldId,
      if (types != null) 'types': types,
    });
    return RecommendationListResponse.fromJson(response.data);
  }

  Future<FieldHealthResponse> getFieldHealth(int fieldId) async {
    final response = await _client.get('/ai/field-health/$fieldId');
    return FieldHealthResponse.fromJson(response.data);
  }

  Future<RiskAssessmentResponse> getCropRisk(int cropCycleId) async {
    final response = await _client.get('/ai/crop-risk/$cropCycleId');
    return RiskAssessmentResponse.fromJson(response.data);
  }
}
