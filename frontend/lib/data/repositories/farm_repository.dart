import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/farm_model.dart';
import '../../core/network/api_client.dart';

final farmRepositoryProvider = Provider<FarmRepository>((ref) {
  return FarmRepository(ref.read(apiClientProvider));
});

class FarmRepository {
  final ApiClient _client;

  FarmRepository(this._client);

  Future<List<FarmModel>> getFarms() async {
    final response = await _client.get('/farms/');
    return (response.data as List).map((e) => FarmModel.fromJson(e)).toList();
  }

  Future<FarmModel> getFarm(int id) async {
    final response = await _client.get('/farms/$id');
    return FarmModel.fromJson(response.data);
  }

  Future<FarmModel> createFarm(Map<String, dynamic> data) async {
    final response = await _client.post('/farms/', data: data);
    return FarmModel.fromJson(response.data);
  }

  Future<FarmModel> updateFarm(int id, Map<String, dynamic> data) async {
    final response = await _client.put('/farms/$id', data: data);
    return FarmModel.fromJson(response.data);
  }

  Future<void> deleteFarm(int id) async {
    await _client.delete('/farms/$id');
  }

  Future<List<FieldModel>> getFields(int farmId) async {
    final response = await _client.get('/farms/$farmId/fields');
    return (response.data as List).map((e) => FieldModel.fromJson(e)).toList();
  }

  Future<FieldModel> getField(int fieldId) async {
    final response = await _client.get('/farms/fields/$fieldId');
    return FieldModel.fromJson(response.data);
  }

  Future<FieldModel> createField(int farmId, Map<String, dynamic> data) async {
    final response = await _client.post('/farms/$farmId/fields', data: data);
    return FieldModel.fromJson(response.data);
  }

  Future<FieldModel> updateField(int fieldId, Map<String, dynamic> data) async {
    final response = await _client.put('/farms/fields/$fieldId', data: data);
    return FieldModel.fromJson(response.data);
  }

  Future<void> deleteField(int fieldId) async {
    await _client.delete('/farms/fields/$fieldId');
  }

  Future<List<CropCycleModel>> getCropCycles({int? fieldId}) async {
    var path = '/farms/crop-cycles';
    if (fieldId != null) {
      path += '?field_id=$fieldId';
    }
    final response = await _client.get(path);
    return (response.data as List).map((e) => CropCycleModel.fromJson(e)).toList();
  }

  Future<CropCycleModel> createCropCycle(int farmId, Map<String, dynamic> data) async {
    final response = await _client.post('/farms/$farmId/crop-cycles', data: data);
    return CropCycleModel.fromJson(response.data);
  }

  Future<DashboardSummaryModel> getDashboard(int farmId) async {
    final response = await _client.get('/farms/$farmId/dashboard');
    return DashboardSummaryModel.fromJson(response.data);
  }

  Future<List<ActivityModel>> getTimeline(int farmId, {int limit = 20}) async {
    final response = await _client.get('/farms/$farmId/timeline?limit=$limit');
    return (response.data as List).map((e) => ActivityModel.fromJson(e)).toList();
  }

  Future<List<UpcomingTaskModel>> getReminders(int farmId) async {
    final response = await _client.get('/farms/$farmId/reminders');
    return (response.data as List).map((e) => UpcomingTaskModel.fromJson(e)).toList();
  }
}
