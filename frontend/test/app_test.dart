import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:agribrain_ai/app.dart';

void main() {
  testWidgets('App renders without error', (tester) async {
    await tester.pumpWidget(
      const ProviderScope(child: AgriBrainApp()),
    );
    expect(find.byType(AgriBrainApp), findsOneWidget);
  });
}
