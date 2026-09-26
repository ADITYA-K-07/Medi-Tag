import 'package:flutter_test/flutter_test.dart';
import 'package:meditag/main.dart';

void main() {
  testWidgets('shows the MediTag foundation screen', (tester) async {
    await tester.pumpWidget(const MediTagApp());

    expect(find.text('MediTag'), findsOneWidget);
    expect(
      find.text('Emergency information when it matters.'),
      findsOneWidget,
    );
    expect(find.text('Session 1 foundation is ready.'), findsOneWidget);
  });
}
