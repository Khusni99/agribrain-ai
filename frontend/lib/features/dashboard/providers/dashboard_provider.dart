import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../data/models/market_price_model.dart';
import '../../../data/repositories/marketplace_repository.dart';

class DashboardState {
  final List<MarketPriceModel> marketPrices;
  final bool isLoading;
  final String? error;

  const DashboardState({
    this.marketPrices = const [],
    this.isLoading = false,
    this.error,
  });

  DashboardState copyWith({
    List<MarketPriceModel>? marketPrices,
    bool? isLoading,
    String? error,
  }) {
    return DashboardState(
      marketPrices: marketPrices ?? this.marketPrices,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class DashboardNotifier extends StateNotifier<DashboardState> {
  final MarketplaceRepository _repo;

  DashboardNotifier(this._repo) : super(const DashboardState());

  Future<void> loadMarketPrices() async {
    state = state.copyWith(isLoading: true);
    try {
      final prices = await _repo.getMarketPrices();
      state = state.copyWith(marketPrices: prices, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }
}

final dashboardProvider = StateNotifierProvider<DashboardNotifier, DashboardState>((ref) {
  return DashboardNotifier(ref.read(marketplaceRepositoryProvider));
});
