import 'package:flutter_test/flutter_test.dart';
import 'package:agribrain_ai/data/models/disease_model.dart';

void main() {
  group('DiseaseModel', () {
    final mockJson = {
      'id': 1,
      'disease_name': 'Anthracnose',
      'confidence': 0.85,
      'severity': 65.0,
      'bounding_boxes': [
        {
          'x1': 10,
          'y1': 20,
          'x2': 100,
          'y2': 150,
          'confidence': 0.92,
          'label': 'Anthracnose',
        }
      ],
      'recommendations': [
        'Semprot fungisida berbahan aktif azoxystrobin 2 ml/L air',
      ],
      'prevention': [
        'Gunakan benih bersertifikat yang tahan penyakit',
      ],
      'economic_risk': {
        'estimated_yield_loss_percent': 39.0,
        'estimated_revenue_loss_per_hectare': 3000000.0,
        'currency': 'IDR',
        'risk_level': 'SEDANG',
      },
      'detection_provider': 'mock-vision-v1',
      'processed_image_width': 640,
      'processed_image_height': 640,
      'created_at': '2026-05-30T10:00:00Z',
    };

    test('fromJson creates DiseaseModel correctly', () {
      final model = DiseaseModel.fromJson(mockJson);

      expect(model.id, 1);
      expect(model.diseaseName, 'Anthracnose');
      expect(model.confidence, 0.85);
      expect(model.severity, 65.0);
      expect(model.boundingBoxes.length, 1);
      expect(model.recommendations.length, 1);
      expect(model.prevention.length, 1);
      expect(model.economicRisk.riskLevel, 'SEDANG');
      expect(model.detectionProvider, 'mock-vision-v1');
      expect(model.processedImageWidth, 640);
      expect(model.processedImageHeight, 640);
      expect(model.createdAt, '2026-05-30T10:00:00Z');
    });

    test('BoundingBox fromJson works', () {
      final boxes = mockJson['bounding_boxes'] as List;
      final box = BoundingBox.fromJson(boxes[0] as Map<String, dynamic>);

      expect(box.x1, 10);
      expect(box.y1, 20);
      expect(box.x2, 100);
      expect(box.y2, 150);
      expect(box.confidence, 0.92);
      expect(box.label, 'Anthracnose');
    });

    test('EconomicRisk fromJson works', () {
      final risk = EconomicRisk.fromJson(mockJson['economic_risk'] as Map<String, dynamic>);

      expect(risk.estimatedYieldLossPercent, 39.0);
      expect(risk.estimatedRevenueLossPerHectare, 3000000.0);
      expect(risk.currency, 'IDR');
      expect(risk.riskLevel, 'SEDANG');
    });

    test('fromJson handles missing optional fields', () {
      final minimalJson = {
        'id': 2,
        'disease_name': 'Healthy',
        'confidence': 0.99,
        'severity': 0.0,
        'bounding_boxes': [],
        'recommendations': [],
        'prevention': [],
        'economic_risk': {
          'estimated_yield_loss_percent': 0.0,
          'estimated_revenue_loss_per_hectare': 0.0,
          'currency': 'IDR',
          'risk_level': 'RENDAH',
        },
      };

      final model = DiseaseModel.fromJson(minimalJson);
      expect(model.diseaseName, 'Healthy');
      expect(model.boundingBoxes, isEmpty);
      expect(model.recommendations, isEmpty);
      expect(model.prevention, isEmpty);
      expect(model.detectionProvider, isNull);
      expect(model.processedImageWidth, isNull);
    });

    test('EconomicRisk uses default currency', () {
      final json = {
        'estimated_yield_loss_percent': 10.0,
        'estimated_revenue_loss_per_hectare': 500000.0,
        'risk_level': 'RENDAH',
      };
      final risk = EconomicRisk.fromJson(json);
      expect(risk.currency, 'IDR');
    });
  });
}
