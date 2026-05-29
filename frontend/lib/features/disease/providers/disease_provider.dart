import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../data/models/disease_model.dart';
import '../../../data/repositories/diagnosis_repository.dart';

class DiseaseState {
  final bool isLoading;
  final File? imageFile;
  final DiseaseModel? result;
  final String? error;

  const DiseaseState({this.isLoading = false, this.imageFile, this.result, this.error});

  DiseaseState copyWith({bool? isLoading, File? imageFile, DiseaseModel? result, String? error}) {
    return DiseaseState(
      isLoading: isLoading ?? this.isLoading,
      imageFile: imageFile ?? this.imageFile,
      result: result ?? this.result,
      error: error,
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
      final result = await _repo.detectDisease(bytes, state.imageFile!.path.split('/').last);
      state = state.copyWith(isLoading: false, result: result);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  void reset() {
    state = const DiseaseState();
  }
}

final diseaseProvider = StateNotifierProvider<DiseaseNotifier, DiseaseState>((ref) {
  return DiseaseNotifier(ref.read(diagnosisRepositoryProvider));
});
