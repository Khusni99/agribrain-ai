import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../features/auth/providers/auth_provider.dart';
import '../features/auth/screens/login_screen.dart';
import '../features/auth/screens/register_screen.dart';
import '../features/splash/splash_screen.dart';
import '../features/dashboard/screens/dashboard_screen.dart';
import '../features/chat/screens/chat_screen.dart';
import '../features/disease/screens/disease_screen.dart';
import '../features/disease/screens/disease_history_screen.dart';
import '../features/cost/screens/cost_screen.dart';
import '../features/marketplace/screens/marketplace_screen.dart';
import '../features/ai/screens/ai_advisor_screen.dart';
import '../features/ai/screens/recommendation_screen.dart';

final goRouterProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authProvider);

  return GoRouter(
    initialLocation: '/splash',
    redirect: (context, state) {
      final loggedIn = authState.status == AuthStatus.authenticated;
      final onAuth = state.matchedLocation == '/login' || state.matchedLocation == '/register';
      final onSplash = state.matchedLocation == '/splash';
      if (onSplash) return null;
      if (!loggedIn && !onAuth) return '/login';
      if (loggedIn && onAuth) return '/dashboard';
      return null;
    },
    routes: [
      GoRoute(path: '/splash', builder: (_, __) => const SplashScreen()),
      GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
      GoRoute(path: '/register', builder: (_, __) => const RegisterScreen()),
      GoRoute(path: '/dashboard', builder: (_, __) => const DashboardScreen()),
      GoRoute(path: '/chat', builder: (_, __) => const ChatScreen()),
      GoRoute(
        path: '/disease',
        builder: (_, __) => const DiseaseScreen(),
        routes: [
          GoRoute(
            path: 'history',
            builder: (_, __) => const DiseaseHistoryScreen(),
          ),
        ],
      ),
      GoRoute(path: '/cost', builder: (_, __) => const CostScreen()),
      GoRoute(path: '/marketplace', builder: (_, __) => const MarketplaceScreen()),
      GoRoute(path: '/ai/advisor', builder: (_, __) => const AIAdvisorScreen()),
      GoRoute(path: '/ai/recommendations', builder: (_, __) => const RecommendationScreen()),
    ],
  );
});
