import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/api_client.dart';
import '../models/cost_model.dart';

final costRepositoryProvider = Provider<CostRepository>((ref) {
  return CostRepository(ref.read(apiClientProvider));
});

class CostRepository {
  final ApiClient _api;

  CostRepository(this._api);

  Future<CostModel> calculate({
    required int fieldId,
    required String cropType,
    required double areaHectare,
    required List<Map<String, dynamic>> items,
  }) async {
    final response = await _api.post('/cost/calculate', data: {
      'field_id': fieldId,
      'crop_type': cropType,
      'area_hectare': areaHectare,
      'items': items,
    });
    return CostModel.fromJson(response.data);
  }
}
