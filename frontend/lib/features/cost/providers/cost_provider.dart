import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../data/models/cost_model.dart';
import '../../../data/repositories/cost_repository.dart';

class CostInput {
  String name;
  String unit;
  double quantity;
  double unitPrice;

  CostInput({
    required this.name,
    required this.unit,
    this.quantity = 1,
    this.unitPrice = 0,
  });

  double get totalCost => quantity * unitPrice;

  Map<String, dynamic> toJson() => {
        'name': name,
        'unit': unit,
        'quantity': quantity,
        'unit_price': unitPrice,
        'total_cost': totalCost,
      };
}

class CostState {
  final List<CostInput> items;
  final double areaHectare;
  final String cropType;
  final bool isLoading;
  final CostModel? result;
  final String? error;

  CostState({
    this.items = const [],
    this.areaHectare = 1.0,
    this.cropType = 'Cabai Merah',
    this.isLoading = false,
    this.result,
    this.error,
  });

  CostState copyWith({
    List<CostInput>? items,
    double? areaHectare,
    String? cropType,
    bool? isLoading,
    CostModel? result,
    String? error,
  }) {
    return CostState(
      items: items ?? this.items,
      areaHectare: areaHectare ?? this.areaHectare,
      cropType: cropType ?? this.cropType,
      isLoading: isLoading ?? this.isLoading,
      result: result ?? this.result,
      error: error,
    );
  }
}

class CostNotifier extends StateNotifier<CostState> {
  final CostRepository _repo;

  static final defaultItems = [
    CostInput(name: 'Benih', unit: 'kg', quantity: 1, unitPrice: 500000),
    CostInput(name: 'Pupuk NPK', unit: 'kg', quantity: 400, unitPrice: 4000),
    CostInput(name: 'Pupuk Urea', unit: 'kg', quantity: 200, unitPrice: 2500),
    CostInput(name: 'Pestisida', unit: 'liter', quantity: 10, unitPrice: 100000),
    CostInput(name: 'Tenaga Kerja', unit: 'HOK', quantity: 50, unitPrice: 75000),
    CostInput(name: 'Irigasi', unit: 'musim', quantity: 1, unitPrice: 500000),
    CostInput(name: 'Transportasi', unit: 'kali', quantity: 1, unitPrice: 300000),
  ];

  CostNotifier(this._repo) : super(CostState(items: defaultItems));

  void updateItem(int index, double quantity, double unitPrice) {
    final items = [...state.items];
    items[index] = CostInput(
      name: items[index].name,
      unit: items[index].unit,
      quantity: quantity,
      unitPrice: unitPrice,
    );
    state = state.copyWith(items: items, result: null);
  }

  void updateArea(double area) {
    state = state.copyWith(areaHectare: area, result: null);
  }

  void updateCropType(String crop) {
    state = state.copyWith(cropType: crop, result: null);
  }

  Future<void> calculate() async {
    state = state.copyWith(isLoading: true, result: null, error: null);
    try {
      final items = state.items.map((e) => e.toJson()).toList();
      final result = await _repo.calculate(
        fieldId: 1,
        cropType: state.cropType,
        areaHectare: state.areaHectare,
        items: items,
      );
      state = state.copyWith(isLoading: false, result: result);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }
}

final costProvider = StateNotifierProvider<CostNotifier, CostState>((ref) {
  return CostNotifier(ref.read(costRepositoryProvider));
});
