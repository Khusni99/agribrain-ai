import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../auth/providers/auth_provider.dart';
import '../providers/dashboard_provider.dart';
import '../widgets/dashboard_card.dart';
import '../widgets/weather_card.dart';
import '../widgets/market_price_preview.dart';
import '../../../core/theme/app_theme.dart';
import '../../farm/screens/farm_list_screen.dart';
import '../../timeline/screens/timeline_screen.dart';
import '../../reminder/screens/reminder_screen.dart';
import '../../ai/screens/ai_advisor_screen.dart';
import '../../ai/screens/recommendation_screen.dart';
import '../../ai/screens/whatsapp_connection_screen.dart';
import '../../ai/screens/notification_settings_screen.dart';

class DashboardScreen extends ConsumerStatefulWidget {
  final int? farmId;
  final int? fieldId;
  final String? fieldName;

  const DashboardScreen({super.key, this.farmId, this.fieldId, this.fieldName});

  @override
  ConsumerState<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends ConsumerState<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() => ref.read(dashboardProvider.notifier).loadAll());
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final dashState = ref.watch(dashboardProvider);
    final auth = ref.watch(authProvider);
    final userName = auth.user?.fullName ?? auth.user?.username ?? 'Petani';
    final summary = dashState.summary;

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('AgriBrain AI', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: theme.colorScheme.primary)),
            Text(widget.fieldName ?? 'Halo, $userName', style: const TextStyle(fontSize: 12, color: Colors.grey)),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.dashboard_outlined),
            tooltip: 'Lahan Saya',
            onPressed: () => Navigator.push(context, MaterialPageRoute(
              builder: (_) => const FarmListScreen(),
            )),
          ),
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
        onRefresh: () async => ref.read(dashboardProvider.notifier).loadAll(),
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
              if (summary != null) ...[
                Row(
                  children: [
                    Expanded(
                      child: DashboardCard(
                        title: 'Lahan Aktif',
                        value: '${summary.totalFarms} Lahan',
                        icon: Icons.terrain,
                        color: AppTheme.primaryGreen,
                        onTap: () => Navigator.push(context, MaterialPageRoute(
                          builder: (_) => const FarmListScreen(),
                        )),
                      ),
                    ),
                    Expanded(
                      child: DashboardCard(
                        title: 'Total Petak',
                        value: '${summary.totalFields} Petak',
                        icon: Icons.grid_view,
                        color: AppTheme.infoBlue,
                        onTap: () {},
                      ),
                    ),
                  ],
                ),
                Row(
                  children: [
                    Expanded(
                      child: DashboardCard(
                        title: 'Musim Tanam Aktif',
                        value: '${summary.activeCropCycles} Aktif',
                        icon: Icons.eco,
                        color: AppTheme.accentOrange,
                        onTap: () {},
                      ),
                    ),
                    Expanded(
                      child: DashboardCard(
                        title: 'Total Panen',
                        value: '${summary.totalHarvestKg.toStringAsFixed(0)} kg',
                        icon: Icons.calendar_view_week,
                        color: AppTheme.primaryGreen,
                        onTap: () {},
                      ),
                    ),
                  ],
                ),
              ] else ...[
                if (dashState.isLoading)
                  const Padding(
                    padding: EdgeInsets.all(16),
                    child: Center(child: CircularProgressIndicator()),
                  )
                else ...[
                  DashboardCard(
                    title: 'Lahan Saya',
                    value: 'Kelola lahan',
                    icon: Icons.terrain,
                    color: AppTheme.primaryGreen,
                    onTap: () => Navigator.push(context, MaterialPageRoute(
                      builder: (_) => const FarmListScreen(),
                    )),
                  ),
                ],
              ],
              if (summary != null && summary.upcomingTasks.isNotEmpty) ...[
                const SizedBox(height: 4),
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
                  child: Row(
                    children: [
                      Text('Pengingat', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                      const Spacer(),
                      TextButton(
                        onPressed: () {
                          if (dashState.farms.isNotEmpty) {
                            Navigator.push(context, MaterialPageRoute(
                              builder: (_) => ReminderScreen(farmId: dashState.farms.first.id),
                            ));
                          }
                        },
                        child: const Text('Lihat Semua'),
                      ),
                    ],
                  ),
                ),
                SizedBox(
                  height: 100,
                  child: ListView.builder(
                    scrollDirection: Axis.horizontal,
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    itemCount: summary.upcomingTasks.length,
                    itemBuilder: (_, i) {
                      final t = summary.upcomingTasks[i];
                      final color = t.priority == 'high' ? AppTheme.dangerRed : AppTheme.accentOrange;
                      return Card(
                        margin: const EdgeInsets.only(right: 12),
                        child: Container(
                          width: 200,
                          padding: const EdgeInsets.all(12),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Icon(Icons.notifications, size: 16, color: color),
                                  const SizedBox(width: 4),
                                  Text(t.taskType, style: TextStyle(fontSize: 11, color: color, fontWeight: FontWeight.w600)),
                                ],
                              ),
                              const SizedBox(height: 4),
                              Text(t.title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                              const Spacer(),
                              Text('Sisa ${t.daysRemaining} hari', style: TextStyle(fontSize: 11, color: Colors.grey.shade600)),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ],
              if (summary != null && summary.cropProgress.isNotEmpty) ...[
                const SizedBox(height: 4),
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
                  child: Text('Progress Tanaman', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                ),
                SizedBox(
                  height: 100,
                  child: ListView.builder(
                    scrollDirection: Axis.horizontal,
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    itemCount: summary.cropProgress.length,
                    itemBuilder: (_, i) {
                      final cp = summary.cropProgress[i];
                      return Card(
                        margin: const EdgeInsets.only(right: 12),
                        child: Container(
                          width: 180,
                          padding: const EdgeInsets.all(12),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(cp.cropName, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                              Text(cp.fieldName, style: TextStyle(fontSize: 11, color: Colors.grey.shade600)),
                              const SizedBox(height: 8),
                              LinearProgressIndicator(
                                value: cp.progressPercentage / 100,
                                backgroundColor: Colors.grey.shade200,
                                color: AppTheme.primaryGreen,
                              ),
                              const SizedBox(height: 4),
                              Text('${cp.progressPercentage.toStringAsFixed(0)}% (hari ke-${cp.daysElapsed})',
                                  style: TextStyle(fontSize: 10, color: Colors.grey.shade600)),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ],
              if (summary != null && summary.recentActivities.isNotEmpty) ...[
                const SizedBox(height: 4),
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
                  child: Row(
                    children: [
                      Text('Aktivitas Terbaru', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                      const Spacer(),
                      TextButton(
                        onPressed: () {
                          if (dashState.farms.isNotEmpty) {
                            Navigator.push(context, MaterialPageRoute(
                              builder: (_) => TimelineScreen(farmId: dashState.farms.first.id),
                            ));
                          }
                        },
                        child: const Text('Lihat Semua'),
                      ),
                    ],
                  ),
                ),
                ...summary.recentActivities.take(3).map((a) => ListTile(
                  dense: true,
                  leading: CircleAvatar(
                    radius: 16,
                    backgroundColor: AppTheme.primaryGreen.withAlpha(30),
                    child: Text(a.activityType.substring(0, 1).toUpperCase(), style: const TextStyle(fontSize: 12)),
                  ),
                  title: Text(a.description, style: const TextStyle(fontSize: 13)),
                  trailing: Text(a.timestamp.length >= 10 ? a.timestamp.substring(0, 10) : '', style: TextStyle(fontSize: 11, color: Colors.grey.shade600)),
                )),
              ],
              const SizedBox(height: 8),
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
                child: Text('Layanan AI', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
              ),
              DashboardCard(
                title: 'Agronomis AI',
                value: 'Tanya saran pertanian',
                icon: Icons.psychology_outlined,
                color: AppTheme.infoBlue,
                onTap: () => Navigator.push(context, MaterialPageRoute(
                  builder: (_) => const AIAdvisorScreen(),
                )),
              ),
              DashboardCard(
                title: 'Rekomendasi AI',
                value: 'Pupuk, semprot, panen',
                icon: Icons.lightbulb_outline,
                color: AppTheme.accentOrange,
                onTap: () => Navigator.push(context, MaterialPageRoute(
                  builder: (_) => const RecommendationScreen(),
                )),
              ),
              DashboardCard(
                title: 'Bot WhatsApp',
                value: 'Tanya via WhatsApp',
                icon: Icons.chat,
                color: const Color(0xFF25D366),
                onTap: () => Navigator.push(context, MaterialPageRoute(
                  builder: (_) => const WhatsAppConnectionScreen(),
                )),
              ),
              DashboardCard(
                title: 'Pengaturan Notif',
                value: 'Atur pengingat',
                icon: Icons.notifications_outlined,
                color: AppTheme.infoBlue,
                onTap: () => Navigator.push(context, MaterialPageRoute(
                  builder: (_) => const NotificationSettingsScreen(),
                )),
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
                color: AppTheme.primaryGreen,
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
