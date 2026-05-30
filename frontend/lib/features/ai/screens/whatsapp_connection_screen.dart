import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../data/repositories/notification_repository.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/widgets/agri_card.dart';
import '../../../core/widgets/loading_view.dart';
import '../../../core/widgets/error_view.dart';

final whatsAppSessionProvider = FutureProvider.autoDispose((ref) async {
  return ref.read(notificationRepositoryProvider).getWhatsAppSession();
});

class WhatsAppConnectionScreen extends ConsumerStatefulWidget {
  const WhatsAppConnectionScreen({super.key});

  @override
  ConsumerState<WhatsAppConnectionScreen> createState() => _WhatsAppConnectionScreenState();
}

class _WhatsAppConnectionScreenState extends ConsumerState<WhatsAppConnectionScreen> {
  final _phoneController = TextEditingController();
  bool _loading = false;

  @override
  void dispose() {
    _phoneController.dispose();
    super.dispose();
  }

  Future<void> _register() async {
    final phone = _phoneController.text.trim();
    if (phone.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Masukkan nomor WhatsApp')),
      );
      return;
    }
    setState(() => _loading = true);
    try {
      await ref.read(notificationRepositoryProvider).registerWhatsApp(phone);
      ref.invalidate(whatsAppSessionProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Nomor $phone berhasil didaftarkan')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Gagal: $e')),
        );
      }
    } finally {
      setState(() => _loading = false);
    }
  }

  Future<void> _unregister() async {
    _phoneController.clear();
    ref.invalidate(whatsAppSessionProvider);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final sessionAsync = ref.watch(whatsAppSessionProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Hubungkan WhatsApp')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          AgriCard(
            color: AppTheme.primaryGreen.withAlpha(8),
            child: Column(
              children: [
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: const Color(0xFF25D366).withAlpha(25),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.chat, size: 48, color: Color(0xFF25D366)),
                ),
                const SizedBox(height: 12),
                Text('WhatsApp Agronomis Bot', style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                Text(
                  'Dapatkan rekomendasi, pengingat, dan saran pertanian langsung ke WhatsApp Anda.',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.grey.shade600, fontSize: 13),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          sessionAsync.when(
            loading: () => const LoadingView(message: 'Memeriksa koneksi...'),
            error: (e, _) => ErrorView(message: 'Gagal memeriksa koneksi: $e', onRetry: () => ref.invalidate(whatsAppSessionProvider)),
            data: (session) {
              if (session.registered && session.phoneNumber != null) {
                return Column(
                  children: [
                    AgriCard(
                      color: AppTheme.primaryGreen.withAlpha(12),
                      child: Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: AppTheme.primaryGreen.withAlpha(25),
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: const Icon(Icons.check_circle, color: AppTheme.primaryGreen, size: 28),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text('Terhubung', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                                Text(session.phoneNumber!, style: TextStyle(color: Colors.grey.shade600, fontSize: 13)),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                    AgriCard(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Perintah yang tersedia', style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
                          const SizedBox(height: 8),
                          _commandItem('/lahan', 'Daftar lahan'),
                          _commandItem('/petak', 'Daftar semua petak'),
                          _commandItem('/petak [nama]', 'Petak di lahan tertentu'),
                          _commandItem('/rekomendasi', 'Rekomendasi hari ini'),
                          _commandItem('/cuaca', 'Info cuaca'),
                          _commandItem('/jadwal', 'Jadwal kegiatan'),
                          _commandItem('/kesehatan', 'Kesehatan tanaman'),
                          const SizedBox(height: 8),
                          Text(
                            'Atau tanya pertanyaan bebas tentang pertanian Anda!',
                            style: TextStyle(fontSize: 12, color: Colors.grey.shade600, fontStyle: FontStyle.italic),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextButton.icon(
                      onPressed: _unregister,
                      icon: const Icon(Icons.link_off, color: AppTheme.dangerRed),
                      label: const Text('Putuskan Koneksi', style: TextStyle(color: AppTheme.dangerRed)),
                      style: TextButton.styleFrom(
                        side: BorderSide(color: AppTheme.dangerRed.withAlpha(60)),
                      ),
                    ),
                  ],
                );
              }
              return Column(
                children: [
                  TextField(
                    controller: _phoneController,
                    keyboardType: TextInputType.phone,
                    decoration: const InputDecoration(
                      labelText: 'Nomor WhatsApp',
                      hintText: '+6281234567890',
                      prefixIcon: Icon(Icons.phone_android),
                    ),
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: FilledButton.icon(
                      onPressed: _loading ? null : _register,
                      icon: _loading
                          ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                          : const Icon(Icons.link),
                      label: const Text('Hubungkan'),
                    ),
                  ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _commandItem(String command, String description) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
            decoration: BoxDecoration(
              color: AppTheme.primaryGreen.withAlpha(20),
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(command, style: TextStyle(fontSize: 11, color: AppTheme.primaryGreen, fontWeight: FontWeight.bold, fontFamily: 'monospace')),
          ),
          const SizedBox(width: 8),
          Expanded(child: Text(description, style: const TextStyle(fontSize: 13))),
        ],
      ),
    );
  }
}
