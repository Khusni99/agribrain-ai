import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/farm_provider.dart';
import '../../../core/theme/app_theme.dart';

class FieldFormScreen extends ConsumerStatefulWidget {
  final int farmId;

  const FieldFormScreen({super.key, required this.farmId});

  @override
  ConsumerState<FieldFormScreen> createState() => _FieldFormScreenState();
}

class _FieldFormScreenState extends ConsumerState<FieldFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameCtrl = TextEditingController();
  final _areaCtrl = TextEditingController();
  final _cropTypeCtrl = TextEditingController();
  final _notesCtrl = TextEditingController();
  bool _saving = false;

  @override
  void dispose() {
    _nameCtrl.dispose();
    _areaCtrl.dispose();
    _cropTypeCtrl.dispose();
    _notesCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Tambah Petak')),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            TextFormField(
              controller: _nameCtrl,
              decoration: const InputDecoration(labelText: 'Nama Petak', prefixIcon: Icon(Icons.grid_view)),
              validator: (v) => v?.isEmpty ?? true ? 'Nama petak wajib diisi' : null,
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _cropTypeCtrl,
              decoration: const InputDecoration(labelText: 'Jenis Tanaman', prefixIcon: Icon(Icons.eco)),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _areaCtrl,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Luas (Ha)', prefixIcon: Icon(Icons.straighten)),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _notesCtrl,
              maxLines: 3,
              decoration: const InputDecoration(labelText: 'Catatan', prefixIcon: Icon(Icons.notes)),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: _saving ? null : _save,
              style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primaryGreen, foregroundColor: Colors.white, padding: const EdgeInsets.symmetric(vertical: 14)),
              child: _saving
                  ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                  : const Text('Simpan', style: TextStyle(fontSize: 16)),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _saving = true);
    try {
      final data = {
        'farm_id': widget.farmId,
        'name': _nameCtrl.text,
        'crop_type': _cropTypeCtrl.text.isEmpty ? null : _cropTypeCtrl.text,
        'area_hectare': double.tryParse(_areaCtrl.text),
        'notes': _notesCtrl.text.isEmpty ? null : _notesCtrl.text,
      }..removeWhere((_, v) => v == null);

      await ref.read(farmsProvider.notifier).createField(widget.farmId, data);
      if (mounted) Navigator.pop(context);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Gagal menyimpan: $e'), backgroundColor: AppTheme.dangerRed),
        );
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }
}
