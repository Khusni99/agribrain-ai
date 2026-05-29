import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/api_client.dart';
import '../models/diagnosis_model.dart';
import '../models/disease_model.dart';

final diagnosisRepositoryProvider = Provider<DiagnosisRepository>((ref) {
  return DiagnosisRepository(ref.read(apiClientProvider));
});

class DiagnosisRepository {
  final ApiClient _api;

  DiagnosisRepository(this._api);

  Future<DiagnosisModel> askAgronomist({
    required String query,
    String? cropType,
    String language = 'id',
    int? fieldId,
  }) async {
    final response = await _api.post('/diagnosis/ask', data: {
      'query': query,
      'crop_type': cropType,
      'language': language,
      'field_id': fieldId,
    });
    return DiagnosisModel.fromJson(response.data);
  }

  Future<DiseaseModel> detectDisease(List<int> imageBytes, String filename) async {
    final response = await _api.uploadBytes('/diagnosis/detect-disease', imageBytes, filename);
    return DiseaseModel.fromJson(response.data);
  }
}
