class CostModel {
  final double costPerPlant;
  final double costPerHectare;
  final double costPerKg;
  final double totalCost;
  final double estimatedRevenue;
  final double profitEstimation;
  final double roiPercentage;
  final List<CostBreakdown> breakdown;

  CostModel({
    required this.costPerPlant,
    required this.costPerHectare,
    required this.costPerKg,
    required this.totalCost,
    required this.estimatedRevenue,
    required this.profitEstimation,
    required this.roiPercentage,
    required this.breakdown,
  });

  factory CostModel.fromJson(Map<String, dynamic> json) {
    return CostModel(
      costPerPlant: (json['cost_per_plant'] as num).toDouble(),
      costPerHectare: (json['cost_per_hectare'] as num).toDouble(),
      costPerKg: (json['cost_per_kg'] as num).toDouble(),
      totalCost: (json['total_cost'] as num).toDouble(),
      estimatedRevenue: (json['estimated_revenue'] as num).toDouble(),
      profitEstimation: (json['profit_estimation'] as num).toDouble(),
      roiPercentage: (json['roi_percentage'] as num).toDouble(),
      breakdown: (json['breakdown'] as List)
          .map((e) => CostBreakdown.fromJson(e))
          .toList(),
    );
  }
}

class CostBreakdown {
  final String category;
  final double quantity;
  final String unit;
  final double unitPrice;
  final double total;
  final double percentage;

  CostBreakdown({
    required this.category,
    required this.quantity,
    required this.unit,
    required this.unitPrice,
    required this.total,
    required this.percentage,
  });

  factory CostBreakdown.fromJson(Map<String, dynamic> json) {
    return CostBreakdown(
      category: json['category'],
      quantity: (json['quantity'] as num).toDouble(),
      unit: json['unit'],
      unitPrice: (json['unit_price'] as num).toDouble(),
      total: (json['total'] as num).toDouble(),
      percentage: (json['percentage'] as num).toDouble(),
    );
  }
}
