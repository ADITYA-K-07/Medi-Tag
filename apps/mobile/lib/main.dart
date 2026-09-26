import 'package:flutter/material.dart';

void main() {
  runApp(const MediTagApp());
}

class MediTagApp extends StatelessWidget {
  const MediTagApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'MediTag',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF006C67)),
        useMaterial3: true,
      ),
      home: const FoundationScreen(),
    );
  }
}

class FoundationScreen extends StatelessWidget {
  const FoundationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('MediTag')),
      body: const Center(
        child: Padding(
          padding: EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.medical_information_outlined, size: 64),
              SizedBox(height: 16),
              Text(
                'Emergency information when it matters.',
                textAlign: TextAlign.center,
              ),
              SizedBox(height: 8),
              Text('Session 1 foundation is ready.'),
            ],
          ),
        ),
      ),
    );
  }
}
