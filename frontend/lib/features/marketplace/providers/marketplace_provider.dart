import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../data/models/product_model.dart';
import '../../../data/models/market_price_model.dart';
import '../../../data/repositories/marketplace_repository.dart';

class MarketplaceState {
  final List<ProductModel> products;
  final List<MarketPriceModel> marketPrices;
  final bool isLoading;
  final String? searchQuery;
  final String? error;

  const MarketplaceState({
    this.products = const [],
    this.marketPrices = const [],
    this.isLoading = false,
    this.searchQuery,
    this.error,
  });

  List<ProductModel> get filteredProducts {
    if (searchQuery == null || searchQuery!.isEmpty) return products;
    final q = searchQuery!.toLowerCase();
    return products.where((p) =>
      p.name.toLowerCase().contains(q) ||
      (p.category?.toLowerCase().contains(q) ?? false)
    ).toList();
  }

  MarketplaceState copyWith({
    List<ProductModel>? products,
    List<MarketPriceModel>? marketPrices,
    bool? isLoading,
    String? searchQuery,
    String? error,
  }) {
    return MarketplaceState(
      products: products ?? this.products,
      marketPrices: marketPrices ?? this.marketPrices,
      isLoading: isLoading ?? this.isLoading,
      searchQuery: searchQuery ?? this.searchQuery,
      error: error,
    );
  }
}

class MarketplaceNotifier extends StateNotifier<MarketplaceState> {
  final MarketplaceRepository _repo;

  MarketplaceNotifier(this._repo) : super(const MarketplaceState());

  Future<void> loadProducts() async {
    state = state.copyWith(isLoading: true);
    try {
      final products = await _repo.getProducts();
      final prices = await _repo.getMarketPrices();
      state = state.copyWith(products: products, marketPrices: prices, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  void search(String query) {
    state = state.copyWith(searchQuery: query);
  }
}

final marketplaceProvider = StateNotifierProvider<MarketplaceNotifier, MarketplaceState>((ref) {
  return MarketplaceNotifier(ref.read(marketplaceRepositoryProvider));
});
