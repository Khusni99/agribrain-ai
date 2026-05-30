class BoundingBox {
  final int x1;
  final int y1;
  final int x2;
  final int y2;
  final double confidence;
  final String label;

  BoundingBox({
    required this.x1,
    required this.y1,
    required this.x2,
    required this.y2,
    required this.confidence,
    required this.label,
  });

  factory BoundingBox.fromJson(Map<String, dynamic> json) {
    return BoundingBox(
      x1: json['x1'] as int,
      y1: json['y1'] as int,
      x2: json['x2'] as int,
      y2: json['y2'] as int,
      confidence: (json['confidence'] as num).toDouble(),
      label: json['label'] as String,
    );
  }
}

class EconomicRisk {
  final double estimatedYieldLossPercent;
  final double estimatedRevenueLossPerHectare;
  final String currency;
  final String riskLevel;

  EconomicRisk({
    required this.estimatedYieldLossPercent,
    required this.estimatedRevenueLossPerHectare,
    this.currency = 'IDR',
    required this.riskLevel,
  });

  factory EconomicRisk.fromJson(Map<String, dynamic> json) {
    return EconomicRisk(
      estimatedYieldLossPercent: (json['estimated_yield_loss_percent'] as num).toDouble(),
      estimatedRevenueLossPerHectare: (json['estimated_revenue_loss_per_hectare'] as num).toDouble(),
      currency: json['currency'] as String? ?? 'IDR',
      riskLevel: json['risk_level'] as String,
    );
  }
}

class DiseaseModel {
  final int id;
  final String diseaseName;
  final double confidence;
  final double severity;
  final List<BoundingBox> boundingBoxes;
  final List<String> recommendations;
  final List<String> prevention;
  final EconomicRisk economicRisk;
  final String? detectionProvider;
  final int? processedImageWidth;
  final int? processedImageHeight;
  final String? createdAt;

  DiseaseModel({
    required this.id,
    required this.diseaseName,
    required this.confidence,
    required this.severity,
    this.boundingBoxes = const [],
    this.recommendations = const [],
    this.prevention = const [],
    required this.economicRisk,
    this.detectionProvider,
    this.processedImageWidth,
    this.processedImageHeight,
    this.createdAt,
  });

  factory DiseaseModel.fromJson(Map<String, dynamic> json) {
    return DiseaseModel(
      id: json['id'] as int,
      diseaseName: json['disease_name'] as String,
      confidence: (json['confidence'] as num).toDouble(),
      severity: (json['severity'] as num).toDouble(),
      boundingBoxes: json['bounding_boxes'] != null
          ? (json['bounding_boxes'] as List)
              .map((e) => BoundingBox.fromJson(e))
              .toList()
          : [],
      recommendations: json['recommendations'] != null
          ? List<String>.from(json['recommendations'])
          : [],
      prevention: json['prevention'] != null
          ? List<String>.from(json['prevention'])
          : [],
      economicRisk: json['economic_risk'] != null
          ? EconomicRisk.fromJson(json['economic_risk'])
          : EconomicRisk(
              estimatedYieldLossPercent: 0,
              estimatedRevenueLossPerHectare: 0,
              riskLevel: 'RENDAH',
            ),
      detectionProvider: json['detection_provider'] as String?,
      processedImageWidth: json['processed_image_width'] as int?,
      processedImageHeight: json['processed_image_height'] as int?,
      createdAt: json['created_at'] as String?,
    );
  }
}
