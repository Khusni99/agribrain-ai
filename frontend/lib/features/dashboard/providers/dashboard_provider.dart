import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../data/models/market_price_model.dart';
import '../../../data/models/farm_model.dart';
import '../../../data/repositories/marketplace_repository.dart';
import '../../../data/repositories/farm_repository.dart';

class DashboardState {
  final List<FarmModel> farms;
  final DashboardSummaryModel? summary;
  final List<MarketPriceModel> marketPrices;
  final bool isLoading;
  final String? error;

  const DashboardState({
    this.farms = const [],
    this.summary,
    this.marketPrices = const [],
    this.isLoading = false,
    this.error,
  });

  DashboardState copyWith({
    List<FarmModel>? farms,
    DashboardSummaryModel? summary,
    List<MarketPriceModel>? marketPrices,
    bool? isLoading,
    String? error,
  }) {
    return DashboardState(
      farms: farms ?? this.farms,
      summary: summary ?? this.summary,
      marketPrices: marketPrices ?? this.marketPrices,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class DashboardNotifier extends StateNotifier<DashboardState> {
  final MarketplaceRepository _marketRepo;
  final FarmRepository _farmRepo;

  DashboardNotifier(this._marketRepo, this._farmRepo) : super(const DashboardState());

  Future<void> loadAll() async {
    state = state.copyWith(isLoading: true);
    try {
      final farms = await _farmRepo.getFarms();
      DashboardSummaryModel? summary;
      if (farms.isNotEmpty) {
        summary = await _farmRepo.getDashboard(farms.first.id);
      }
      final prices = await _marketRepo.getMarketPrices();
      state = state.copyWith(farms: farms, summary: summary, marketPrices: prices, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }
}

final dashboardProvider = StateNotifierProvider<DashboardNotifier, DashboardState>((ref) {
  return DashboardNotifier(ref.read(marketplaceRepositoryProvider), ref.read(farmRepositoryProvider));
});
