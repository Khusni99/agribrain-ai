class FarmModel {
  final int id;
  final String name;
  final String? location;
  final double? latitude;
  final double? longitude;
  final double? altitude;
  final double? areaHectare;
  final String? soilType;
  final double? soilPh;
  final String? description;
  final String createdAt;
  final String? updatedAt;
  final int fieldsCount;

  FarmModel({
    required this.id,
    required this.name,
    this.location,
    this.latitude,
    this.longitude,
    this.altitude,
    this.areaHectare,
    this.soilType,
    this.soilPh,
    this.description,
    required this.createdAt,
    this.updatedAt,
    this.fieldsCount = 0,
  });

  factory FarmModel.fromJson(Map<String, dynamic> json) {
    return FarmModel(
      id: json['id'] as int,
      name: json['name'] as String,
      location: json['location'] as String?,
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
      altitude: (json['altitude'] as num?)?.toDouble(),
      areaHectare: (json['area_hectare'] as num?)?.toDouble(),
      soilType: json['soil_type'] as String?,
      soilPh: (json['soil_ph'] as num?)?.toDouble(),
      description: json['description'] as String?,
      createdAt: json['created_at'] as String,
      updatedAt: json['updated_at'] as String?,
      fieldsCount: json['fields_count'] as int? ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'location': location,
      'latitude': latitude,
      'longitude': longitude,
      'altitude': altitude,
      'area_hectare': areaHectare,
      'soil_type': soilType,
      'soil_ph': soilPh,
      'description': description,
    };
  }
}

class FieldModel {
  final int id;
  final int farmId;
  final String name;
  final double? areaHectare;
  final String? cropType;
  final String? plantingDate;
  final String status;
  final String? notes;

  FieldModel({
    required this.id,
    required this.farmId,
    required this.name,
    this.areaHectare,
    this.cropType,
    this.plantingDate,
    this.status = 'active',
    this.notes,
  });

  factory FieldModel.fromJson(Map<String, dynamic> json) {
    return FieldModel(
      id: json['id'] as int,
      farmId: json['farm_id'] as int,
      name: json['name'] as String,
      areaHectare: (json['area_hectare'] as num?)?.toDouble(),
      cropType: json['crop_type'] as String?,
      plantingDate: json['planting_date'] as String?,
      status: json['status'] as String? ?? 'active',
      notes: json['notes'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'farm_id': farmId,
      'name': name,
      'area_hectare': areaHectare,
      'crop_type': cropType,
      'planting_date': plantingDate,
      'status': status,
      'notes': notes,
    };
  }
}

class CropCycleModel {
  final int id;
  final int fieldId;
  final int cropId;
  final String startDate;
  final String? expectedHarvestDate;
  final String? actualHarvestDate;
  final int? plantCount;
  final double? spacingMeters;
  final String status;

  CropCycleModel({
    required this.id,
    required this.fieldId,
    required this.cropId,
    required this.startDate,
    this.expectedHarvestDate,
    this.actualHarvestDate,
    this.plantCount,
    this.spacingMeters,
    this.status = 'active',
  });

  factory CropCycleModel.fromJson(Map<String, dynamic> json) {
    return CropCycleModel(
      id: json['id'] as int,
      fieldId: json['field_id'] as int,
      cropId: json['crop_id'] as int,
      startDate: json['start_date'] as String,
      expectedHarvestDate: json['expected_harvest_date'] as String?,
      actualHarvestDate: json['actual_harvest_date'] as String?,
      plantCount: json['plant_count'] as int?,
      spacingMeters: (json['spacing_meters'] as num?)?.toDouble(),
      status: json['status'] as String? ?? 'active',
    );
  }
}

class DashboardSummaryModel {
  final int totalFarms;
  final int totalFields;
  final int activeCropCycles;
  final double totalHarvestKg;
  final List<ActivityModel> recentActivities;
  final List<UpcomingTaskModel> upcomingTasks;
  final List<CropProgressModel> cropProgress;

  DashboardSummaryModel({
    required this.totalFarms,
    required this.totalFields,
    required this.activeCropCycles,
    required this.totalHarvestKg,
    required this.recentActivities,
    required this.upcomingTasks,
    required this.cropProgress,
  });

  factory DashboardSummaryModel.fromJson(Map<String, dynamic> json) {
    return DashboardSummaryModel(
      totalFarms: json['total_farms'] as int? ?? 0,
      totalFields: json['total_fields'] as int? ?? 0,
      activeCropCycles: json['active_crop_cycles'] as int? ?? 0,
      totalHarvestKg: (json['total_harvest_kg'] as num?)?.toDouble() ?? 0,
      recentActivities: (json['recent_activities'] as List? ?? [])
          .map((e) => ActivityModel.fromJson(e))
          .toList(),
      upcomingTasks: (json['upcoming_tasks'] as List? ?? [])
          .map((e) => UpcomingTaskModel.fromJson(e))
          .toList(),
      cropProgress: (json['crop_progress'] as List? ?? [])
          .map((e) => CropProgressModel.fromJson(e))
          .toList(),
    );
  }
}

class ActivityModel {
  final int id;
  final String activityType;
  final String description;
  final String? fieldName;
  final String timestamp;

  ActivityModel({
    required this.id,
    required this.activityType,
    required this.description,
    this.fieldName,
    required this.timestamp,
  });

  factory ActivityModel.fromJson(Map<String, dynamic> json) {
    return ActivityModel(
      id: json['id'] as int,
      activityType: json['activity_type'] as String,
      description: json['description'] as String,
      fieldName: json['field_name'] as String?,
      timestamp: json['timestamp'] as String,
    );
  }
}

class UpcomingTaskModel {
  final int id;
  final String taskType;
  final String title;
  final String? description;
  final String? fieldName;
  final String dueDate;
  final int daysRemaining;
  final String priority;

  UpcomingTaskModel({
    required this.id,
    required this.taskType,
    required this.title,
    this.description,
    this.fieldName,
    required this.dueDate,
    required this.daysRemaining,
    required this.priority,
  });

  factory UpcomingTaskModel.fromJson(Map<String, dynamic> json) {
    return UpcomingTaskModel(
      id: json['id'] as int,
      taskType: json['task_type'] as String,
      title: json['title'] as String,
      description: json['description'] as String?,
      fieldName: json['field_name'] as String?,
      dueDate: json['due_date'] as String,
      daysRemaining: json['days_remaining'] as int? ?? 0,
      priority: json['priority'] as String? ?? 'medium',
    );
  }
}

class CropProgressModel {
  final int cycleId;
  final String cropName;
  final String fieldName;
  final String startDate;
  final String? expectedHarvestDate;
  final int daysElapsed;
  final int totalDays;
  final double progressPercentage;
  final String status;

  CropProgressModel({
    required this.cycleId,
    required this.cropName,
    required this.fieldName,
    required this.startDate,
    this.expectedHarvestDate,
    required this.daysElapsed,
    required this.totalDays,
    required this.progressPercentage,
    required this.status,
  });

  factory CropProgressModel.fromJson(Map<String, dynamic> json) {
    return CropProgressModel(
      cycleId: json['cycle_id'] as int,
      cropName: json['crop_name'] as String,
      fieldName: json['field_name'] as String,
      startDate: json['start_date'] as String,
      expectedHarvestDate: json['expected_harvest_date'] as String?,
      daysElapsed: json['days_elapsed'] as int? ?? 0,
      totalDays: json['total_days'] as int? ?? 1,
      progressPercentage: (json['progress_percentage'] as num?)?.toDouble() ?? 0,
      status: json['status'] as String? ?? 'active',
    );
  }
}
