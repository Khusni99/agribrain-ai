class AIAdvisorResponse {
  final String advice;
  final FieldHealthResponse? fieldHealth;
  final RecommendationListResponse? recommendations;
  final RiskAssessmentResponse? risks;

  AIAdvisorResponse({
    required this.advice,
    this.fieldHealth,
    this.recommendations,
    this.risks,
  });

  factory AIAdvisorResponse.fromJson(Map<String, dynamic> json) {
    return AIAdvisorResponse(
      advice: json['advice'] as String? ?? '',
      fieldHealth: json['field_health'] != null
          ? FieldHealthResponse.fromJson(json['field_health'])
          : null,
      recommendations: json['recommendations'] != null
          ? RecommendationListResponse.fromJson(json['recommendations'])
          : null,
      risks: json['risks'] != null
          ? RiskAssessmentResponse.fromJson(json['risks'])
          : null,
    );
  }
}

class FieldHealthResponse {
  final int fieldId;
  final String fieldName;
  final double healthScore;
  final List<HealthFactor> factors;
  final RiskFactor diseaseRisk;
  final RiskFactor nutrientRisk;
  final YieldForecast yieldForecast;
  final String status;

  FieldHealthResponse({
    required this.fieldId,
    required this.fieldName,
    required this.healthScore,
    required this.factors,
    required this.diseaseRisk,
    required this.nutrientRisk,
    required this.yieldForecast,
    required this.status,
  });

  factory FieldHealthResponse.fromJson(Map<String, dynamic> json) {
    return FieldHealthResponse(
      fieldId: json['field_id'] as int? ?? 0,
      fieldName: json['field_name'] as String? ?? '',
      healthScore: (json['health_score'] as num?)?.toDouble() ?? 0,
      factors: (json['factors'] as List? ?? [])
          .map((e) => HealthFactor.fromJson(e))
          .toList(),
      diseaseRisk: RiskFactor.fromJson(json['disease_risk'] ?? {}),
      nutrientRisk: RiskFactor.fromJson(json['nutrient_risk'] ?? {}),
      yieldForecast: YieldForecast.fromJson(json['yield_forecast'] ?? {}),
      status: json['status'] as String? ?? 'unknown',
    );
  }
}

class HealthFactor {
  final String factor;
  final String impact;
  final String? severity;

  HealthFactor({required this.factor, required this.impact, this.severity});

  factory HealthFactor.fromJson(Map<String, dynamic> json) {
    return HealthFactor(
      factor: json['factor'] as String? ?? '',
      impact: json['impact'] as String? ?? '',
      severity: json['severity'] as String?,
    );
  }
}

class RiskFactor {
  final double score;
  final String level;
  final String description;
  final List<String> contributingFactors;
  final List<String> recommendations;

  RiskFactor({
    required this.score,
    required this.level,
    required this.description,
    this.contributingFactors = const [],
    this.recommendations = const [],
  });

  factory RiskFactor.fromJson(Map<String, dynamic> json) {
    return RiskFactor(
      score: (json['score'] as num?)?.toDouble() ?? 0,
      level: json['level'] as String? ?? 'RENDAH',
      description: json['description'] as String? ?? '',
      contributingFactors: (json['contributing_factors'] as List? ?? [])
          .map((e) => e.toString())
          .toList(),
      recommendations: (json['recommendations'] as List? ?? [])
          .map((e) => e.toString())
          .toList(),
    );
  }
}

class YieldForecast {
  final double predictedYieldKg;
  final double predictedYieldPerHectare;
  final Map<String, dynamic> confidenceRange;
  final double predictedRevenue;
  final List<Map<String, dynamic>> factors;

  YieldForecast({
    required this.predictedYieldKg,
    required this.predictedYieldPerHectare,
    required this.confidenceRange,
    required this.predictedRevenue,
    required this.factors,
  });

  factory YieldForecast.fromJson(Map<String, dynamic> json) {
    return YieldForecast(
      predictedYieldKg: (json['predicted_yield_kg'] as num?)?.toDouble() ?? 0,
      predictedYieldPerHectare: (json['predicted_yield_per_hectare'] as num?)?.toDouble() ?? 0,
      confidenceRange: json['confidence_range'] as Map<String, dynamic>? ?? {},
      predictedRevenue: (json['predicted_revenue'] as num?)?.toDouble() ?? 0,
      factors: (json['factors'] as List? ?? []).map((e) => Map<String, dynamic>.from(e)).toList(),
    );
  }
}

class RecommendationListResponse {
  final List<RecommendationItem> today;
  final List<RecommendationItem> thisWeek;
  final List<RecommendationItem> urgent;
  final List<RecommendationItem> all;

  RecommendationListResponse({
    this.today = const [],
    this.thisWeek = const [],
    this.urgent = const [],
    this.all = const [],
  });

  factory RecommendationListResponse.fromJson(Map<String, dynamic> json) {
    return RecommendationListResponse(
      today: (json['today'] as List? ?? [])
          .map((e) => RecommendationItem.fromJson(e))
          .toList(),
      thisWeek: (json['this_week'] as List? ?? [])
          .map((e) => RecommendationItem.fromJson(e))
          .toList(),
      urgent: (json['urgent'] as List? ?? [])
          .map((e) => RecommendationItem.fromJson(e))
          .toList(),
      all: (json['all'] as List? ?? [])
          .map((e) => RecommendationItem.fromJson(e))
          .toList(),
    );
  }
}

class RecommendationItem {
  final String type;
  final String title;
  final String description;
  final String priority;
  final String? timing;
  final String? dosage;
  final String? method;
  final String reasoning;

  RecommendationItem({
    required this.type,
    required this.title,
    required this.description,
    required this.priority,
    this.timing,
    this.dosage,
    this.method,
    required this.reasoning,
  });

  factory RecommendationItem.fromJson(Map<String, dynamic> json) {
    return RecommendationItem(
      type: json['type'] as String? ?? '',
      title: json['title'] as String? ?? '',
      description: json['description'] as String? ?? '',
      priority: json['priority'] as String? ?? 'medium',
      timing: json['timing'] as String?,
      dosage: json['dosage'] as String?,
      method: json['method'] as String?,
      reasoning: json['reasoning'] as String? ?? '',
    );
  }
}

class RiskAssessmentResponse {
  final RiskFactor diseaseRisk;
  final RiskFactor nutrientDeficiencyRisk;
  final RiskFactor yieldReductionRisk;
  final double overallRiskScore;
  final String overallRiskLevel;

  RiskAssessmentResponse({
    required this.diseaseRisk,
    required this.nutrientDeficiencyRisk,
    required this.yieldReductionRisk,
    required this.overallRiskScore,
    required this.overallRiskLevel,
  });

  factory RiskAssessmentResponse.fromJson(Map<String, dynamic> json) {
    return RiskAssessmentResponse(
      diseaseRisk: RiskFactor.fromJson(json['disease_risk'] ?? {}),
      nutrientDeficiencyRisk: RiskFactor.fromJson(json['nutrient_deficiency_risk'] ?? {}),
      yieldReductionRisk: RiskFactor.fromJson(json['yield_reduction_risk'] ?? {}),
      overallRiskScore: (json['overall_risk_score'] as num?)?.toDouble() ?? 0,
      overallRiskLevel: json['overall_risk_level'] as String? ?? 'RENDAH',
    );
  }
}
