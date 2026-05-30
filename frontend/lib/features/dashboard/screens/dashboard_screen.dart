import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../auth/providers/auth_provider.dart';
import '../providers/dashboard_provider.dart';
import '../widgets/dashboard_card.dart';
import '../widgets/weather_card.dart';
import '../widgets/market_price_preview.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/widgets/loading_view.dart';
import '../../../core/widgets/error_view.dart';
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
            Text('AgriBrain AI',
                style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: theme.colorScheme.primary)),
            Text(widget.fieldName ?? 'Halo, $userName',
                style: const TextStyle(fontSize: 12, color: Colors.grey)),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.dashboard_outlined),
            tooltip: 'Lahan Saya',
            onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                    builder: (_) => const FarmListScreen())),
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
        child: dashState.isLoading && summary == null
            ? const LoadingView(message: 'Memuat dashboard...')
            : dashState.error != null && summary == null
                ? ErrorView(
                    message: dashState.error!,
                    onRetry: () => ref.read(dashboardProvider.notifier).loadAll(),
                  )
                : ListView(
                    physics: const AlwaysScrollableScrollPhysics(),
                    padding: const EdgeInsets.fromLTRB(16, 8, 16, 80),
                    children: [
                      SectionHeader(title: 'Ringkasan'),
                      if (summary != null) ...[
                        Row(
                          children: [
                            Expanded(
                              child: DashboardCard(
                                title: 'Lahan Aktif',
                                value: '${summary.totalFarms} Lahan',
                                icon: Icons.terrain,
                                color: AppTheme.primaryGreen,
                                onTap: () => Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                        builder: (_) =>
                                            const FarmListScreen())),
                              ),
                            ),
                            const SizedBox(width: 12),
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
                        const SizedBox(height: 12),
                        Row(
                          children: [
                            Expanded(
                              child: DashboardCard(
                                title: 'Musim Tanam',
                                value: '${summary.activeCropCycles} Aktif',
                                icon: Icons.eco,
                                color: AppTheme.accentOrange,
                                onTap: () {},
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: DashboardCard(
                                title: 'Total Panen',
                                value:
                                    '${summary.totalHarvestKg.toStringAsFixed(0)} kg',
                                icon: Icons.calendar_view_week,
                                color: AppTheme.secondaryGreen,
                                onTap: () {},
                              ),
                            ),
                          ],
                        ),
                      ],
                      if (summary == null)
                        DashboardCard(
                          title: 'Lahan Saya',
                          value: 'Kelola lahan',
                          icon: Icons.terrain,
                          color: AppTheme.primaryGreen,
                          onTap: () => Navigator.push(
                              context,
                              MaterialPageRoute(
                                  builder: (_) => const FarmListScreen())),
                        ),
                      if (summary != null &&
                          summary.upcomingTasks.isNotEmpty) ...[
                        const SizedBox(height: 8),
                        SectionHeader(
                          title: 'Pengingat',
                          action: TextButton(
                            onPressed: () {
                              if (dashState.farms.isNotEmpty) {
                                Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                        builder: (_) => ReminderScreen(
                                            farmId:
                                                dashState.farms.first.id)));
                              }
                            },
                            child: const Text('Lihat Semua',
                                style: TextStyle(fontSize: 12)),
                          ),
                        ),
                        SizedBox(
                          height: 100,
                          child: ListView.builder(
                            scrollDirection: Axis.horizontal,
                            itemCount: summary.upcomingTasks.length,
                            itemBuilder: (_, i) {
                              final t = summary.upcomingTasks[i];
                              final color = t.priority == 'high'
                                  ? AppTheme.dangerRed
                                  : AppTheme.accentOrange;
                              return Container(
                                width: 200,
                                margin: const EdgeInsets.only(right: 12),
                                child: Card(
                                  child: Padding(
                                    padding: const EdgeInsets.all(12),
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Row(
                                          children: [
                                            Icon(Icons.notifications,
                                                size: 16, color: color),
                                            const SizedBox(width: 4),
                                            Text(t.taskType,
                                                style: TextStyle(
                                                    fontSize: 11,
                                                    color: color,
                                                    fontWeight:
                                                        FontWeight.w600)),
                                          ],
                                        ),
                                        const SizedBox(height: 4),
                                        Text(t.title,
                                            style: const TextStyle(
                                                fontWeight: FontWeight.bold,
                                                fontSize: 13)),
                                        const Spacer(),
                                        Text(
                                          'Sisa ${t.daysRemaining} hari',
                                          style: TextStyle(
                                              fontSize: 11,
                                              color: Colors.grey.shade600),
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                              );
                            },
                          ),
                        ),
                      ],
                      if (summary != null &&
                          summary.cropProgress.isNotEmpty) ...[
                        const SizedBox(height: 8),
                        SectionHeader(title: 'Progress Tanaman'),
                        SizedBox(
                          height: 110,
                          child: ListView.builder(
                            scrollDirection: Axis.horizontal,
                            itemCount: summary.cropProgress.length,
                            itemBuilder: (_, i) {
                              final cp = summary.cropProgress[i];
                              return Container(
                                width: 180,
                                margin: const EdgeInsets.only(right: 12),
                                child: Card(
                                  child: Padding(
                                    padding: const EdgeInsets.all(12),
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Text(cp.cropName,
                                            style: const TextStyle(
                                                fontWeight: FontWeight.bold,
                                                fontSize: 13)),
                                        Text(cp.fieldName,
                                            style: TextStyle(
                                                fontSize: 11,
                                                color: Colors.grey.shade600)),
                                        const Spacer(),
                                        ClipRRect(
                                          borderRadius:
                                              BorderRadius.circular(4),
                                          child: LinearProgressIndicator(
                                            value: cp.progressPercentage / 100,
                                            minHeight: 6,
                                            backgroundColor:
                                                Colors.grey.shade200,
                                            color: AppTheme.primaryGreen,
                                          ),
                                        ),
                                        const SizedBox(height: 4),
                                        Text(
                                          '${cp.progressPercentage.toStringAsFixed(0)}% (hari ke-${cp.daysElapsed})',
                                          style: TextStyle(
                                              fontSize: 10,
                                              color: Colors.grey.shade600),
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                              );
                            },
                          ),
                        ),
                      ],
                      if (summary != null &&
                          summary.recentActivities.isNotEmpty) ...[
                        const SizedBox(height: 8),
                        SectionHeader(
                          title: 'Aktivitas Terbaru',
                          action: TextButton(
                            onPressed: () {
                              if (dashState.farms.isNotEmpty) {
                                Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                        builder: (_) => TimelineScreen(
                                            farmId:
                                                dashState.farms.first.id)));
                              }
                            },
                            child: const Text('Lihat Semua',
                                style: TextStyle(fontSize: 12)),
                          ),
                        ),
                        Card(
                          child: Column(
                            children: summary.recentActivities
                                .take(3)
                                .map((a) => ListTile(
                                      dense: true,
                                      leading: CircleAvatar(
                                        radius: 16,
                                        backgroundColor:
                                            AppTheme.primaryGreen.withAlpha(25),
                                        child: Text(
                                          a.activityType
                                              .substring(0, 1)
                                              .toUpperCase(),
                                          style: const TextStyle(
                                              fontSize: 12,
                                              fontWeight: FontWeight.w600,
                                              color: AppTheme.primaryGreen),
                                        ),
                                      ),
                                      title: Text(a.description,
                                          style:
                                              const TextStyle(fontSize: 13)),
                                      trailing: Text(
                                        a.timestamp.length >= 10
                                            ? a.timestamp.substring(0, 10)
                                            : '',
                                        style: TextStyle(
                                            fontSize: 11,
                                            color: Colors.grey.shade600),
                                      ),
                                    ))
                                .toList(),
                          ),
                        ),
                      ],
                      const SizedBox(height: 8),
                      SectionHeader(title: 'Layanan AI'),
                      DashboardCard(
                        title: 'Agronomis AI',
                        value: 'Tanya saran pertanian',
                        icon: Icons.psychology_outlined,
                        color: AppTheme.infoBlue,
                        onTap: () => Navigator.push(
                            context,
                            MaterialPageRoute(
                                builder: (_) => const AIAdvisorScreen())),
                      ),
                      DashboardCard(
                        title: 'Rekomendasi AI',
                        value: 'Pupuk, semprot, panen',
                        icon: Icons.lightbulb_outline,
                        color: AppTheme.accentOrange,
                        onTap: () => Navigator.push(
                            context,
                            MaterialPageRoute(
                                builder: (_) =>
                                    const RecommendationScreen())),
                      ),
                      DashboardCard(
                        title: 'Bot WhatsApp',
                        value: 'Tanya via WhatsApp',
                        icon: Icons.chat,
                        color: AppTheme.whatsappGreen,
                        onTap: () => Navigator.push(
                            context,
                            MaterialPageRoute(
                                builder: (_) =>
                                    const WhatsAppConnectionScreen())),
                      ),
                      DashboardCard(
                        title: 'Pengaturan Notif',
                        value: 'Atur pengingat',
                        icon: Icons.notifications_outlined,
                        color: AppTheme.infoBlue,
                        onTap: () => Navigator.push(
                            context,
                            MaterialPageRoute(
                                builder: (_) =>
                                    const NotificationSettingsScreen())),
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
                      SectionHeader(title: 'Informasi'),
                      const WeatherCard(
                        temperature: 28.5,
                        humidity: 82,
                        rainfall: 5.2,
                        condition: 'Cerah Berawan',
                        riskLevel: 'SEDANG',
                      ),
                      MarketPricePreview(prices: dashState.marketPrices),
                    ],
                  ),
      ),
      bottomNavigationBar: _BottomNav(selectedIndex: 0),
    );
  }
}

class SectionHeader extends StatelessWidget {
  final String title;
  final Widget? action;

  const SectionHeader({super.key, required this.title, this.action});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.fromLTRB(4, 8, 4, 8),
      child: Row(
        children: [
          Text(title,
              style: theme.textTheme.titleSmall
                  ?.copyWith(fontWeight: FontWeight.bold)),
          if (action != null) ...[
            const Spacer(),
            action!,
          ],
        ],
      ),
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
          case 0:
            context.go('/dashboard');
          case 1:
            context.push('/chat');
          case 2:
            context.push('/marketplace');
        }
      },
      destinations: const [
        NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home),
            label: 'Beranda'),
        NavigationDestination(
            icon: Icon(Icons.chat_outlined),
            selectedIcon: Icon(Icons.chat),
            label: 'AI Chat'),
        NavigationDestination(
            icon: Icon(Icons.store_outlined),
            selectedIcon: Icon(Icons.store),
            label: 'Pasar'),
      ],
    );
  }
}
