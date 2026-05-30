import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/marketplace_provider.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/widgets/empty_state.dart';

class MarketplaceScreen extends ConsumerStatefulWidget {
  const MarketplaceScreen({super.key});

  @override
  ConsumerState<MarketplaceScreen> createState() => _MarketplaceScreenState();
}

class _MarketplaceScreenState extends ConsumerState<MarketplaceScreen> {
  final _searchCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    Future.microtask(() => ref.read(marketplaceProvider.notifier).loadProducts());
  }

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(marketplaceProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Pasar Tani')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              controller: _searchCtrl,
              decoration: InputDecoration(
                hintText: 'Cari produk...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchCtrl.text.isNotEmpty
                    ? IconButton(icon: const Icon(Icons.clear), onPressed: () {
                        _searchCtrl.clear();
                        ref.read(marketplaceProvider.notifier).search('');
                      })
                    : null,
              ),
              onChanged: (v) => ref.read(marketplaceProvider.notifier).search(v),
            ),
          ),
          if (state.isLoading)
            const Expanded(child: Center(child: CircularProgressIndicator()))
          else if (state.filteredProducts.isEmpty)
            Expanded(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const EmptyState(
                    icon: Icons.store_mall_directory_outlined,
                    title: 'Belum ada produk',
                  ),
                  FilledButton(
                    onPressed: () => ref.read(marketplaceProvider.notifier).loadProducts(),
                    child: const Text('Muat Ulang'),
                  ),
                ],
              ),
            )
          else
            Expanded(
              child: RefreshIndicator(
                onRefresh: () => ref.read(marketplaceProvider.notifier).loadProducts(),
                child: ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  itemCount: state.filteredProducts.length,
                  itemBuilder: (ctx, i) {
                    final p = state.filteredProducts[i];
                    return Card(
                      margin: const EdgeInsets.only(bottom: 8),
                      child: InkWell(
                        borderRadius: BorderRadius.circular(16),
                        onTap: () => _showDetail(context, p),
                        child: Padding(
                          padding: const EdgeInsets.all(12),
                          child: Row(
                            children: [
                              Container(
                                width: 56, height: 56,
                                decoration: BoxDecoration(
                                  color: AppTheme.cardGreen,
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: Icon(
                                  p.category == 'hortikultura' ? Icons.eco : Icons.grass,
                                  color: AppTheme.primaryGreen,
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(p.name, style: const TextStyle(fontWeight: FontWeight.bold)),
                                    if (p.quantityKg != null)
                                      Text('${p.quantityKg!.toStringAsFixed(0)} kg', style: const TextStyle(color: Colors.grey, fontSize: 12)),
                                    if (p.location != null)
                                      Row(
                                        children: [
                                          const Icon(Icons.location_on, size: 12, color: Colors.grey),
                                          const SizedBox(width: 2),
                                          Text(p.location!, style: const TextStyle(color: Colors.grey, fontSize: 11)),
                                        ],
                                      ),
                                  ],
                                ),
                              ),
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.end,
                                children: [
                                  Text(p.formattedPrice, style: const TextStyle(fontWeight: FontWeight.bold, color: AppTheme.primaryGreen)),
                                  Text(p.status, style: const TextStyle(fontSize: 11, color: Colors.grey)),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),
            ),
        ],
      ),
    );
  }

  void _showDetail(BuildContext context, dynamic product) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(child: Container(width: 40, height: 4, decoration: BoxDecoration(color: Colors.grey.shade300, borderRadius: BorderRadius.circular(2)))),
            const SizedBox(height: 16),
            Text(product.name, style: Theme.of(ctx).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            if (product.quantityKg != null) Text('Jumlah: ${product.quantityKg!.toStringAsFixed(0)} kg'),
            if (product.pricePerKg != null) Text('Harga: Rp ${product.pricePerKg!.toStringAsFixed(0)}/kg', style: const TextStyle(fontWeight: FontWeight.bold)),
            if (product.location != null) Text('Lokasi: ${product.location}'),
            if (product.qualityGrade != null) Text('Grade: ${product.qualityGrade}'),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () => Navigator.pop(ctx),
                child: const Text('Hubungi Penjual'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
