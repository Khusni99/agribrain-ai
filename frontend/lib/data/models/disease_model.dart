class DiseaseModel {
  final String diseaseName;
  final double severityPercentage;
  final double confidenceScore;
  final List<String> treatmentRecommendations;
  final EconomicImpact? economicImpact;

  DiseaseModel({
    required this.diseaseName,
    required this.severityPercentage,
    required this.confidenceScore,
    required this.treatmentRecommendations,
    this.economicImpact,
  });

  factory DiseaseModel.fromJson(Map<String, dynamic> json) {
    return DiseaseModel(
      diseaseName: json['disease_name'],
      severityPercentage: (json['severity_percentage'] as num).toDouble(),
      confidenceScore: (json['confidence_score'] as num).toDouble(),
      treatmentRecommendations: List<String>.from(json['treatment_recommendations']),
      economicImpact: json['economic_impact'] != null
          ? EconomicImpact.fromJson(json['economic_impact'])
          : null,
    );
  }
}

class EconomicImpact {
  final double estimatedYieldLossPercent;
  final double estimatedRevenueLossPerHectare;

  EconomicImpact({
    required this.estimatedYieldLossPercent,
    required this.estimatedRevenueLossPerHectare,
  });

  factory EconomicImpact.fromJson(Map<String, dynamic> json) {
    return EconomicImpact(
      estimatedYieldLossPercent: (json['estimated_yield_loss_percent'] as num).toDouble(),
      estimatedRevenueLossPerHectare:
          (json['estimated_revenue_loss_per_hectare'] as num).toDouble(),
    );
  }
}
