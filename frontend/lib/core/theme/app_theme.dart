import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  static const Color primaryGreen = Color(0xFF2E7D32);
  static const Color primaryDark = Color(0xFF1B5E20);
  static const Color primaryLight = Color(0xFFA5D6A7);
  static const Color secondaryGreen = Color(0xFF558B2F);
  static const Color accentOrange = Color(0xFFFF8F00);
  static const Color accentYellow = Color(0xFFF9A825);
  static const Color dangerRed = Color(0xFFD32F2F);
  static const Color warningYellow = Color(0xFFFBC02D);
  static const Color infoBlue = Color(0xFF1976D2);
  static const Color surfaceLight = Color(0xFFF1F8E9);
  static const Color cardGreen = Color(0xFFE8F5E9);
  static const Color offWhite = Color(0xFFFAFAF5);
  static const Color whatsappGreen = Color(0xFF25D366);

  static const double cardRadius = 16;
  static const double buttonRadius = 12;
  static const double inputRadius = 12;
  static const double spacingXs = 4;
  static const double spacingSm = 8;
  static const double spacingMd = 16;
  static const double spacingLg = 24;
  static const double spacingXl = 32;

  static ThemeData get lightTheme {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: primaryGreen,
      brightness: Brightness.light,
      primary: primaryGreen,
      secondary: secondaryGreen,
      tertiary: accentYellow,
      error: dangerRed,
      surface: offWhite,
    );
    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      textTheme: GoogleFonts.interTextTheme().copyWith(
        headlineLarge: GoogleFonts.inter(fontWeight: FontWeight.w700, fontSize: 28),
        headlineMedium: GoogleFonts.inter(fontWeight: FontWeight.w700, fontSize: 24),
        headlineSmall: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 20),
        titleLarge: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 18),
        titleMedium: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 16),
        titleSmall: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 14),
        bodyLarge: GoogleFonts.inter(fontSize: 16),
        bodyMedium: GoogleFonts.inter(fontSize: 14),
        bodySmall: GoogleFonts.inter(fontSize: 12, color: Colors.grey.shade600),
        labelLarge: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 14),
        labelSmall: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.w500),
      ),
      appBarTheme: AppBarTheme(
        centerTitle: true,
        elevation: 0,
        scrolledUnderElevation: 1,
        backgroundColor: colorScheme.surface,
        foregroundColor: colorScheme.primary,
        titleTextStyle: GoogleFonts.inter(
          fontSize: 18,
          fontWeight: FontWeight.w600,
          color: colorScheme.primary,
        ),
      ),
      cardTheme: CardThemeData(
        elevation: 1,
        shadowColor: Colors.black.withAlpha(20),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(cardRadius),
        ),
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
        clipBehavior: Clip.antiAlias,
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: colorScheme.surfaceContainerHighest.withAlpha(100),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(inputRadius),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(inputRadius),
          borderSide: BorderSide(color: Colors.grey.shade300, width: 1),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(inputRadius),
          borderSide: BorderSide(color: primaryGreen, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(inputRadius),
          borderSide: BorderSide(color: dangerRed, width: 1),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        prefixIconColor: Colors.grey.shade600,
        labelStyle: GoogleFonts.inter(color: Colors.grey.shade600, fontSize: 14),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          minimumSize: const Size(double.infinity, 48),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(buttonRadius),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          textStyle: GoogleFonts.inter(
            fontSize: 15,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          minimumSize: const Size(double.infinity, 48),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(buttonRadius),
          ),
          side: BorderSide(color: primaryGreen.withAlpha(80)),
          textStyle: GoogleFonts.inter(
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      navigationBarTheme: NavigationBarThemeData(
        elevation: 3,
        shadowColor: Colors.black.withAlpha(30),
        indicatorColor: primaryGreen.withAlpha(30),
        labelTextStyle: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return GoogleFonts.inter(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: primaryGreen,
            );
          }
          return GoogleFonts.inter(
            fontSize: 12,
            color: Colors.grey.shade600,
          );
        }),
        iconTheme: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return IconThemeData(color: primaryGreen, size: 24);
          }
          return IconThemeData(color: Colors.grey.shade600, size: 24);
        }),
      ),
      dividerTheme: DividerThemeData(
        space: 0,
        thickness: 1,
        color: Colors.grey.shade200,
      ),
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
      chipTheme: ChipThemeData(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      ),
      scaffoldBackgroundColor: offWhite,
    );
  }

  static ThemeData get darkTheme {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: primaryGreen,
      brightness: Brightness.dark,
      primary: primaryLight,
    );
    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      textTheme: GoogleFonts.interTextTheme(ThemeData.dark().textTheme),
      scaffoldBackgroundColor: const Color(0xFF121212),
    );
  }
}
