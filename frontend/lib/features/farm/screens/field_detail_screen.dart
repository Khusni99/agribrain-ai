import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../data/models/farm_model.dart';
import '../../../core/theme/app_theme.dart';
import '../../dashboard/screens/dashboard_screen.dart';
import '../../timeline/screens/timeline_screen.dart';
import '../../ai/screens/field_health_screen.dart';

class FieldDetailScreen extends ConsumerWidget {
  final FarmModel farm;
  final FieldModel field;

  const FieldDetailScreen({super.key, required this.farm, required this.field});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: Text(field.name)),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            color: AppTheme.surfaceLight,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Informasi Petak', style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 12),
                  _infoRow('Nama Petak', field.name),
                  _infoRow('Jenis Tanaman', field.cropType ?? '-'),
                  _infoRow('Luas', field.areaHectare != null ? '${field.areaHectare!.toStringAsFixed(1)} Ha' : '-'),
                  _infoRow('Status', field.status == 'active' ? 'Aktif' : 'Nonaktif'),
                  _infoRow('Tanggal Tanam', field.plantingDate ?? '-'),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _ActionButton(
                  icon: Icons.add,
                  label: 'Catat Aktivitas',
                  color: AppTheme.primaryGreen,
                  onTap: () => _showRecordSheet(context),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _ActionButton(
                  icon: Icons.pan_tool,
                  label: 'Catat Panen',
                  color: AppTheme.accentOrange,
                  onTap: () => _showHarvestSheet(context),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: _ActionButton(
                  icon: Icons.favorite_outline,
                  label: 'Kesehatan',
                  color: AppTheme.dangerRed,
                  onTap: () => Navigator.push(context, MaterialPageRoute(
                    builder: (_) => FieldHealthScreen(fieldId: field.id, fieldName: field.name),
                  )),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _ActionButton(
                  icon: Icons.history,
                  label: 'Timeline',
                  color: AppTheme.infoBlue,
                  onTap: () => Navigator.push(context, MaterialPageRoute(
                    builder: (_) => TimelineScreen(farmId: farm.id),
                  )),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: _ActionButton(
                  icon: Icons.eco,
                  label: 'Progress',
                  color: AppTheme.primaryGreen,
                  onTap: () => Navigator.push(context, MaterialPageRoute(
                    builder: (_) => DashboardScreen(farmId: farm.id, fieldId: field.id, fieldName: field.name),
                  )),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text('Aktivitas Terbaru', style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          const Card(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Text('Data aktivitas akan ditampilkan di sini', style: TextStyle(color: Colors.grey)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _infoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          SizedBox(width: 120, child: Text(label, style: TextStyle(color: Colors.grey.shade600, fontSize: 13))),
          Expanded(child: Text(value, style: const TextStyle(fontWeight: FontWeight.w500, fontSize: 13))),
        ],
      ),
    );
  }

  void _showRecordSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Catat Aktivitas', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 16),
            ListTile(
              leading: const Icon(Icons.eco, color: AppTheme.primaryGreen),
              title: const Text('Pemupukan'),
              onTap: () { Navigator.pop(ctx); _showFertilizerForm(context); },
            ),
            ListTile(
              leading: const Icon(Icons.water_drop, color: AppTheme.infoBlue),
              title: const Text('Penyemprotan'),
              onTap: () { Navigator.pop(ctx); _showSprayForm(context); },
            ),
            ListTile(
              leading: const Icon(Icons.warning_amber, color: AppTheme.dangerRed),
              title: const Text('Hama & Penyakit'),
              onTap: () { Navigator.pop(ctx); _showDiseaseForm(context); },
            ),
          ],
        ),
      ),
    );
  }

  void _showFertilizerForm(BuildContext context) {
    Navigator.push(context, MaterialPageRoute(
      builder: (_) => _RecordForm(
        title: 'Catat Pemupukan',
        fields: ['Jenis Pupuk', 'Dosis (kg/Ha)', 'Cara Aplikasi', 'Tahap Tanam'],
        hints: ['Urea, NPK, ...', '200', 'Tabur/Semprot', 'Vegetatif Awal'],
        icon: Icons.eco,
        onSave: (v) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Catatan pupuk berhasil disimpan')),
          );
        },
      ),
    ));
  }

  void _showSprayForm(BuildContext context) {
    Navigator.push(context, MaterialPageRoute(
      builder: (_) => _RecordForm(
        title: 'Catat Penyemprotan',
        fields: ['Nama Produk', 'Dosis', 'Target Hama', 'Metode'],
        hints: ['Antracol, ...', '2 ml/L', 'Jamur/Hama', 'Semprot'],
        icon: Icons.water_drop,
        onSave: (v) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Catatan semprot berhasil disimpan')),
          );
        },
      ),
    ));
  }

  void _showDiseaseForm(BuildContext context) {
    Navigator.push(context, MaterialPageRoute(
      builder: (_) => _RecordForm(
        title: 'Catat Hama & Penyakit',
        fields: ['Nama Penyakit', 'Tingkat Keparahan (%)', 'Gejala', 'Tindakan'],
        hints: ['Layu Bakteri', '30', 'Daun menguning', 'Semprot fungisida'],
        icon: Icons.warning_amber,
        onSave: (v) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Catatan penyakit berhasil disimpan')),
          );
        },
      ),
    ));
  }

  void _showHarvestSheet(BuildContext context) {
    Navigator.push(context, MaterialPageRoute(
      builder: (_) => _RecordForm(
        title: 'Catat Panen',
        fields: ['Jumlah Panen (kg)', 'Harga Rata-rata (Rp)', 'Grade', 'Catatan'],
        hints: ['500', '10000', 'A/B/C', 'Hasil panen hari ini'],
        icon: Icons.pan_tool,
        onSave: (v) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Catatan panen berhasil disimpan')),
          );
        },
      ),
    ));
  }
}

class _ActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _ActionButton({required this.icon, required this.label, required this.color, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 16),
          child: Column(
            children: [
              Icon(icon, color: color, size: 28),
              const SizedBox(height: 4),
              Text(label, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: color)),
            ],
          ),
        ),
      ),
    );
  }
}

class _RecordForm extends StatefulWidget {
  final String title;
  final List<String> fields;
  final List<String> hints;
  final IconData icon;
  final Function(Map<String, String>) onSave;

  const _RecordForm({required this.title, required this.fields, required this.hints, required this.icon, required this.onSave});

  @override
  State<_RecordForm> createState() => _RecordFormState();
}

class _RecordFormState extends State<_RecordForm> {
  final _controllers = <TextEditingController>[];

  @override
  void initState() {
    super.initState();
    for (var i = 0; i < widget.fields.length; i++) {
      _controllers.add(TextEditingController());
    }
  }

  @override
  void dispose() {
    for (final c in _controllers) {
      c.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.title)),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          for (var i = 0; i < widget.fields.length; i++) ...[
            if (i > 0) const SizedBox(height: 12),
            TextFormField(
              controller: _controllers[i],
              decoration: InputDecoration(
                labelText: widget.fields[i],
                hintText: widget.hints[i],
                prefixIcon: Icon(widget.icon),
              ),
            ),
          ],
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: () {
              final data = <String, String>{};
              for (var i = 0; i < widget.fields.length; i++) {
                data[widget.fields[i]] = _controllers[i].text;
              }
              widget.onSave(data);
              Navigator.pop(context);
            },
            style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primaryGreen, foregroundColor: Colors.white, padding: const EdgeInsets.symmetric(vertical: 14)),
            child: const Text('Simpan', style: TextStyle(fontSize: 16)),
          ),
        ],
      ),
    );
  }
}
