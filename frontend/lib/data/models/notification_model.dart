class NotificationLogModel {
  final int id;
  final String notificationType;
  final String title;
  final String message;
  final String status;
  final String sentAt;

  NotificationLogModel({
    required this.id,
    required this.notificationType,
    required this.title,
    required this.message,
    required this.status,
    required this.sentAt,
  });

  factory NotificationLogModel.fromJson(Map<String, dynamic> json) {
    return NotificationLogModel(
      id: json['id'] as int? ?? 0,
      notificationType: json['notification_type'] as String? ?? '',
      title: json['title'] as String? ?? '',
      message: json['message'] as String? ?? '',
      status: json['status'] as String? ?? 'sent',
      sentAt: json['sent_at'] as String? ?? '',
    );
  }
}

class ReminderPreferenceModel {
  final bool whatsappEnabled;
  final bool fertilizerReminder;
  final bool sprayReminder;
  final bool harvestReminder;
  final bool diseaseRiskAlert;
  final bool weatherAlert;
  final String reminderTimeStart;
  final String reminderTimeEnd;
  final int advanceDaysFertilizer;
  final int advanceDaysSpray;
  final int advanceDaysHarvest;

  ReminderPreferenceModel({
    required this.whatsappEnabled,
    required this.fertilizerReminder,
    required this.sprayReminder,
    required this.harvestReminder,
    required this.diseaseRiskAlert,
    required this.weatherAlert,
    required this.reminderTimeStart,
    required this.reminderTimeEnd,
    required this.advanceDaysFertilizer,
    required this.advanceDaysSpray,
    required this.advanceDaysHarvest,
  });

  factory ReminderPreferenceModel.fromJson(Map<String, dynamic> json) {
    return ReminderPreferenceModel(
      whatsappEnabled: json['whatsapp_enabled'] as bool? ?? true,
      fertilizerReminder: json['fertilizer_reminder'] as bool? ?? true,
      sprayReminder: json['spray_reminder'] as bool? ?? true,
      harvestReminder: json['harvest_reminder'] as bool? ?? true,
      diseaseRiskAlert: json['disease_risk_alert'] as bool? ?? true,
      weatherAlert: json['weather_alert'] as bool? ?? false,
      reminderTimeStart: json['reminder_time_start'] as String? ?? '06:00',
      reminderTimeEnd: json['reminder_time_end'] as String? ?? '18:00',
      advanceDaysFertilizer: json['advance_days_fertilizer'] as int? ?? 1,
      advanceDaysSpray: json['advance_days_spray'] as int? ?? 1,
      advanceDaysHarvest: json['advance_days_harvest'] as int? ?? 3,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'whatsapp_enabled': whatsappEnabled,
      'fertilizer_reminder': fertilizerReminder,
      'spray_reminder': sprayReminder,
      'harvest_reminder': harvestReminder,
      'disease_risk_alert': diseaseRiskAlert,
      'weather_alert': weatherAlert,
      'reminder_time_start': reminderTimeStart,
      'reminder_time_end': reminderTimeEnd,
      'advance_days_fertilizer': advanceDaysFertilizer,
      'advance_days_spray': advanceDaysSpray,
      'advance_days_harvest': advanceDaysHarvest,
    };
  }
}

class WhatsAppSessionModel {
  final bool registered;
  final String? phoneNumber;
  final bool? isVerified;
  final String? provider;

  WhatsAppSessionModel({
    required this.registered,
    this.phoneNumber,
    this.isVerified,
    this.provider,
  });

  factory WhatsAppSessionModel.fromJson(Map<String, dynamic> json) {
    return WhatsAppSessionModel(
      registered: json['registered'] as bool? ?? false,
      phoneNumber: json['phone_number'] as String?,
      isVerified: json['is_verified'] as bool?,
      provider: json['provider'] as String?,
    );
  }
}
