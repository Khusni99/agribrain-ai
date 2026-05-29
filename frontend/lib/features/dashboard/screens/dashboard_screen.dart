import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../auth/providers/auth_provider.dart';
import '../providers/dashboard_provider.dart';
import '../widgets/dashboard_card.dart';
import '../widgets/weather_card.dart';
import '../widgets/market_price_preview.dart';
import '../../../core/theme/app_theme.dart';

class DashboardScreen extends ConsumerStatefulWidget {
  const DashboardScreen({super.key});

  @override
  ConsumerState<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends ConsumerState<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() => ref.read(dashboardProvider.notifier).loadMarketPrices());
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final dashState = ref.watch(dashboardProvider);
    final auth = ref.watch(authProvider);
    final userName = auth.user?.fullName ?? auth.user?.username ?? 'Petani';

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('AgriBrain AI', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: theme.colorScheme.primary)),
            Text('Halo, $userName', style: const TextStyle(fontSize: 12, color: Colors.grey)),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout_rounded),
            onPressed: () async {
              await ref.read(authProvider.notifier).logout();
              if (context.mounted) context.go('/login');
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async => ref.read(dashboardProvider.notifier).loadMarketPrices(),
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.only(bottom: 24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
                child: Text('Ringkasan', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
              ),
              DashboardCard(
                title: 'Lahan Aktif',
                value: '2 Bidang',
                icon: Icons.terrain,
                color: AppTheme.primaryGreen,
                onTap: () => _showComingSoon(context, 'Manajemen Lahan'),
              ),
              DashboardCard(
                title: 'Tugas Hari Ini',
                value: '3 Tugas',
                icon: Icons.checklist,
                color: AppTheme.accentOrange,
                onTap: () => _showComingSoon(context, 'Tugas'),
              ),
              const SizedBox(height: 8),
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
                child: Text('Layanan AI', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
              ),
              DashboardCard(
                title: 'Tanya Agronomis AI',
                value: 'Diagnosis tanaman',
                icon: Icons.chat_bubble_outline,
                color: AppTheme.infoBlue,
                onTap: () => context.push('/chat'),
              ),
              DashboardCard(
                title: 'Deteksi Penyakit',
                value: 'Upload foto tanaman',
                icon: Icons.document_scanner,
                color: AppTheme.dangerRed,
                onTap: () => context.push('/disease'),
              ),
              DashboardCard(
                title: 'Kalkulator Biaya',
                value: 'Hitung biaya produksi',
                icon: Icons.calculate_outlined,
                color: AppTheme.accentOrange,
                onTap: () => context.push('/cost'),
              ),
              const SizedBox(height: 8),
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
                child: Text('Informasi', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
              ),
              const WeatherCard(
                temperature: 28.5,
                humidity: 82,
                rainfall: 5.2,
                condition: 'Cerah Berawan',
                riskLevel: 'SEDANG',
              ),
              if (dashState.isLoading)
                const Center(child: CircularProgressIndicator())
              else
                MarketPricePreview(prices: dashState.marketPrices),
              const SizedBox(height: 80),
            ],
          ),
        ),
      ),
      bottomNavigationBar: _BottomNav(selectedIndex: 0),
    );
  }

  void _showComingSoon(BuildContext context, String feature) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('$feature - Segera hadir')),
    );
  }
}

class _BottomNav extends StatelessWidget {
  final int selectedIndex;
  const _BottomNav({required this.selectedIndex});

  @override
  Widget build(BuildContext context) {
    return NavigationBar(
      selectedIndex: selectedIndex,
      onDestinationSelected: (i) {
        switch (i) {
          case 0: context.go('/dashboard');
          case 1: context.push('/chat');
          case 2: context.push('/marketplace');
        }
      },
      destinations: const [
        NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Beranda'),
        NavigationDestination(icon: Icon(Icons.chat_outlined), selectedIcon: Icon(Icons.chat), label: 'AI Chat'),
        NavigationDestination(icon: Icon(Icons.store_outlined), selectedIcon: Icon(Icons.store), label: 'Pasar'),
      ],
    );
  }
}
