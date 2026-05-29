import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/farm_provider.dart';
import '../../../data/models/farm_model.dart';
import '../../../core/theme/app_theme.dart';

class FarmFormScreen extends ConsumerStatefulWidget {
  final FarmModel? farm;

  const FarmFormScreen({super.key, this.farm});

  @override
  ConsumerState<FarmFormScreen> createState() => _FarmFormScreenState();
}

class _FarmFormScreenState extends ConsumerState<FarmFormScreen> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _nameCtrl;
  late final TextEditingController _locationCtrl;
  late final TextEditingController _areaCtrl;
  late final TextEditingController _soilTypeCtrl;
  late final TextEditingController _soilPhCtrl;
  late final TextEditingController _descCtrl;
  bool _saving = false;

  bool get _isEdit => widget.farm != null;

  @override
  void initState() {
    super.initState();
    final f = widget.farm;
    _nameCtrl = TextEditingController(text: f?.name ?? '');
    _locationCtrl = TextEditingController(text: f?.location ?? '');
    _areaCtrl = TextEditingController(text: f?.areaHectare?.toString() ?? '');
    _soilTypeCtrl = TextEditingController(text: f?.soilType ?? '');
    _soilPhCtrl = TextEditingController(text: f?.soilPh?.toString() ?? '');
    _descCtrl = TextEditingController(text: f?.description ?? '');
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    _locationCtrl.dispose();
    _areaCtrl.dispose();
    _soilTypeCtrl.dispose();
    _soilPhCtrl.dispose();
    _descCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(_isEdit ? 'Edit Lahan' : 'Tambah Lahan')),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            TextFormField(
              controller: _nameCtrl,
              decoration: const InputDecoration(labelText: 'Nama Lahan', prefixIcon: Icon(Icons.agriculture)),
              validator: (v) => v?.isEmpty ?? true ? 'Nama lahan wajib diisi' : null,
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _locationCtrl,
              decoration: const InputDecoration(labelText: 'Lokasi', prefixIcon: Icon(Icons.location_on)),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _areaCtrl,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Luas Lahan (Ha)', prefixIcon: Icon(Icons.straighten)),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _soilTypeCtrl,
              decoration: const InputDecoration(labelText: 'Jenis Tanah', prefixIcon: Icon(Icons.layers)),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _soilPhCtrl,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'pH Tanah', prefixIcon: Icon(Icons.science)),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _descCtrl,
              maxLines: 3,
              decoration: const InputDecoration(labelText: 'Catatan', prefixIcon: Icon(Icons.notes)),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: _saving ? null : _save,
              style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primaryGreen, foregroundColor: Colors.white, padding: const EdgeInsets.symmetric(vertical: 14)),
              child: _saving
                  ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                  : Text(_isEdit ? 'Simpan' : 'Tambah Lahan', style: const TextStyle(fontSize: 16)),
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
        'name': _nameCtrl.text,
        'location': _locationCtrl.text.isEmpty ? null : _locationCtrl.text,
        'area_hectare': double.tryParse(_areaCtrl.text),
        'soil_type': _soilTypeCtrl.text.isEmpty ? null : _soilTypeCtrl.text,
        'soil_ph': double.tryParse(_soilPhCtrl.text),
        'description': _descCtrl.text.isEmpty ? null : _descCtrl.text,
      }..removeWhere((_, v) => v == null);

      final notifier = ref.read(farmsProvider.notifier);
      if (_isEdit) {
        await notifier.update(widget.farm!.id, data);
      } else {
        await notifier.create(data);
      }
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
