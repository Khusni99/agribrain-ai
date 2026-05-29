class ProductModel {
  final int id;
  final int userId;
  final String name;
  final String? category;
  final double? quantityKg;
  final double? pricePerKg;
  final String? qualityGrade;
  final String? location;
  final String status;
  final String createdAt;

  ProductModel({
    required this.id,
    required this.userId,
    required this.name,
    this.category,
    this.quantityKg,
    this.pricePerKg,
    this.qualityGrade,
    this.location,
    required this.status,
    required this.createdAt,
  });

  factory ProductModel.fromJson(Map<String, dynamic> json) {
    return ProductModel(
      id: json['id'],
      userId: json['user_id'],
      name: json['name'],
      category: json['category'],
      quantityKg: (json['quantity_kg'] as num?)?.toDouble(),
      pricePerKg: (json['price_per_kg'] as num?)?.toDouble(),
      qualityGrade: json['quality_grade'],
      location: json['location'],
      status: json['status'],
      createdAt: json['created_at'],
    );
  }

  String get formattedPrice => pricePerKg != null
      ? 'Rp ${pricePerKg!.toStringAsFixed(0)}'
      : 'Hubungi';
}
