class DiagnosisModel {
  final String diagnosis;
  final List<PossibleCause> possibleCauses;
  final List<String> recommendedActions;
  final List<FertilizerRec>? fertilizerRecommendations;
  final List<SprayRec>? sprayRecommendations;
  final double confidenceScore;
  final List<String> followUpQuestions;

  DiagnosisModel({
    required this.diagnosis,
    required this.possibleCauses,
    required this.recommendedActions,
    this.fertilizerRecommendations,
    this.sprayRecommendations,
    required this.confidenceScore,
    required this.followUpQuestions,
  });

  factory DiagnosisModel.fromJson(Map<String, dynamic> json) {
    return DiagnosisModel(
      diagnosis: json['diagnosis'],
      possibleCauses: (json['possible_causes'] as List)
          .map((e) => PossibleCause.fromJson(e))
          .toList(),
      recommendedActions: List<String>.from(json['recommended_actions']),
      fertilizerRecommendations: json['fertilizer_recommendations'] != null
          ? (json['fertilizer_recommendations'] as List)
              .map((e) => FertilizerRec.fromJson(e))
              .toList()
          : null,
      sprayRecommendations: json['spray_recommendations'] != null
          ? (json['spray_recommendations'] as List)
              .map((e) => SprayRec.fromJson(e))
              .toList()
          : null,
      confidenceScore: (json['confidence_score'] as num).toDouble(),
      followUpQuestions: List<String>.from(json['follow_up_questions']),
    );
  }
}

class PossibleCause {
  final String cause;
  final double confidence;
  final String action;

  PossibleCause({
    required this.cause,
    required this.confidence,
    required this.action,
  });

  factory PossibleCause.fromJson(Map<String, dynamic> json) {
    return PossibleCause(
      cause: json['cause'],
      confidence: (json['confidence'] as num).toDouble(),
      action: json['action'],
    );
  }
}

class FertilizerRec {
  final String type;
  final String dosage;
  final String timing;

  FertilizerRec({required this.type, required this.dosage, required this.timing});

  factory FertilizerRec.fromJson(Map<String, dynamic> json) {
    return FertilizerRec(
      type: json['type'],
      dosage: json['dosage'],
      timing: json['timing'],
    );
  }
}

class SprayRec {
  final String product;
  final String activeIngredient;
  final String dosage;

  SprayRec({required this.product, required this.activeIngredient, required this.dosage});

  factory SprayRec.fromJson(Map<String, dynamic> json) {
    return SprayRec(
      product: json['product'],
      activeIngredient: json['active_ingredient'],
      dosage: json['dosage'],
    );
  }
}
