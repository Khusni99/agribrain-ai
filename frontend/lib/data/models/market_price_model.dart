class MarketPriceModel {
  final int id;
  final String commodity;
  final String? location;
  final double? minPrice;
  final double? maxPrice;
  final double? avgPrice;
  final String? trend;
  final String? source;
  final String recordedAt;

  MarketPriceModel({
    required this.id,
    required this.commodity,
    this.location,
    this.minPrice,
    this.maxPrice,
    this.avgPrice,
    this.trend,
    this.source,
    required this.recordedAt,
  });

  factory MarketPriceModel.fromJson(Map<String, dynamic> json) {
    return MarketPriceModel(
      id: json['id'],
      commodity: json['commodity'],
      location: json['location'],
      minPrice: (json['min_price'] as num?)?.toDouble(),
      maxPrice: (json['max_price'] as num?)?.toDouble(),
      avgPrice: (json['avg_price'] as num?)?.toDouble(),
      trend: json['trend'],
      source: json['source'],
      recordedAt: json['recorded_at'],
    );
  }
}
