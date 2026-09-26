# ADR 0002: Use Flutter for the Android application

Status: accepted

Build one Android-only Flutter application for unauthenticated, citizen, and
doctor experiences. Flutter replaces the React Native choice in the original
brief. Platform-specific NFC code stays behind a small service interface when it
is introduced, keeping screens easy to read and test.
