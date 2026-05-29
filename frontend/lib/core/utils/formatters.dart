import 'package:intl/intl.dart';

class Formatters {
  static String currency(double amount) {
    final fmt = NumberFormat('#,###', 'id_ID');
    return 'Rp ${fmt.format(amount)}';
  }

  static String percentage(double value) {
    return '${value.toStringAsFixed(1)}%';
  }

  static String decimal(double value, {int digits = 1}) {
    return value.toStringAsFixed(digits);
  }

  static String date(String dateStr) {
    try {
      final dt = DateTime.parse(dateStr);
      return DateFormat('dd MMM yyyy', 'id').format(dt);
    } catch (_) {
      return dateStr;
    }
  }

  static String dateTime(String dateStr) {
    try {
      final dt = DateTime.parse(dateStr);
      return DateFormat('dd MMM yyyy HH:mm', 'id').format(dt);
    } catch (_) {
      return dateStr;
    }
  }
}
