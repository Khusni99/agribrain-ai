import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/api_client.dart';
import '../models/product_model.dart';
import '../models/market_price_model.dart';

final marketplaceRepositoryProvider = Provider<MarketplaceRepository>((ref) {
  return MarketplaceRepository(ref.read(apiClientProvider));
});

class MarketplaceRepository {
  final ApiClient _api;

  MarketplaceRepository(this._api);

  Future<List<ProductModel>> getProducts({String? category}) async {
    final response = await _api.get('/marketplace/products',
        queryParams: category != null ? {'category': category} : null);
    return (response.data as List).map((e) => ProductModel.fromJson(e)).toList();
  }

  Future<List<MarketPriceModel>> getMarketPrices({String? commodity}) async {
    final response = await _api.get('/marketplace/prices',
        queryParams: commodity != null ? {'commodity': commodity} : null);
    return (response.data as List).map((e) => MarketPriceModel.fromJson(e)).toList();
  }
}
