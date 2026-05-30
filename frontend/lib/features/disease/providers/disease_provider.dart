import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../data/models/disease_model.dart';
import '../../../data/repositories/diagnosis_repository.dart';

class DiseaseState {
  final bool isLoading;
  final File? imageFile;
  final DiseaseModel? result;
  final String? error;
  final List<DiseaseModel> history;
  final bool historyLoading;

  const DiseaseState({
    this.isLoading = false,
    this.imageFile,
    this.result,
    this.error,
    this.history = const [],
    this.historyLoading = false,
  });

  DiseaseState copyWith({
    bool? isLoading,
    File? imageFile,
    DiseaseModel? result,
    String? error,
    List<DiseaseModel>? history,
    bool? historyLoading,
  }) {
    return DiseaseState(
      isLoading: isLoading ?? this.isLoading,
      imageFile: imageFile ?? this.imageFile,
      result: result ?? this.result,
      error: error,
      history: history ?? this.history,
      historyLoading: historyLoading ?? this.historyLoading,
    );
  }
}

class DiseaseNotifier extends StateNotifier<DiseaseState> {
  final DiagnosisRepository _repo;

  DiseaseNotifier(this._repo) : super(const DiseaseState());

  void setImage(File file) {
    state = state.copyWith(imageFile: file, result: null, error: null);
  }

  Future<void> detect() async {
    if (state.imageFile == null) return;
    state = state.copyWith(isLoading: true, result: null, error: null);
    try {
      final bytes = await state.imageFile!.readAsBytes();
      final filename = state.imageFile!.path.split(RegExp(r'[/\\]')).last;
      final result = await _repo.detectDisease(bytes, filename);
      state = state.copyWith(isLoading: false, result: result);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> loadHistory() async {
    state = state.copyWith(historyLoading: true);
    try {
      final history = await _repo.getDetectionHistory();
      state = state.copyWith(historyLoading: false, history: history);
    } catch (e) {
      state = state.copyWith(historyLoading: false, error: e.toString());
    }
  }

  void reset() {
    state = const DiseaseState();
  }
}

final diseaseProvider = StateNotifierProvider<DiseaseNotifier, DiseaseState>((ref) {
  return DiseaseNotifier(ref.read(diagnosisRepositoryProvider));
});
