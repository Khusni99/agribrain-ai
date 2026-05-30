# AgriBrain AI - Release APK

## Build Command

```bash
# Development (local backend on emulator):
flutter build apk --release --dart-define=API_BASE_URL=http://10.0.2.2:8000

# Production:
flutter build apk --release --dart-define=API_BASE_URL=https://api.agribrain.ai
```

## Output APK Path

```
frontend/build/app/outputs/flutter-apk/app-release.apk
```

## Install Instructions

1. **Enable installation from unknown sources** on the Android device:
   - Settings → Security → Install unknown apps → File manager → Allow

2. Transfer the APK to the device:
   - USB: `adb install frontend/build/app/outputs/flutter-apk/app-release.apk`
   - Or copy via cloud/email and open the file on the device

3. The app requires Android 5.0 (API 21) or higher.

4. **Backend:** The APK must connect to a running backend server.
   - Local testing: `http://10.0.2.2:8000` (Android emulator → host machine)
   - Real device: Use `http://<your-ip>:8000` with `--dart-define=API_BASE_URL=...`

## Common Build Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Daemon compilation failed` | Kotlin incremental cache corruption | Run `flutter clean` and rebuild |
| `Keystore file not found` | Missing or wrong keystore path | Ensure `android/app/release-keystore.jks` exists and `android/key.properties` is correct |
| `No internet access in APK` | Missing INTERNET permission | Already added to `AndroidManifest.xml`; verify in `android/app/src/main/` |
| `Cleartext HTTP traffic not allowed` | Android 9+ blocks HTTP | Uses `android:usesCleartextTraffic="true"` in manifest; use HTTPS for production with `--dart-define` |
| App shows blank white screen | Backend URL wrong or backend not running | Verify `--dart-define=API_BASE_URL=<url>` is correct; check backend is running |

## Environment Config

The app uses `--dart-define` for API base URL configuration:

- **Debug mode (default):** `http://10.0.2.2:8000` (Android emulator to host)
- **Release mode (required):** Must pass `--dart-define=API_BASE_URL=<url>`
- Override in any mode: `--dart-define=API_BASE_URL=<url>`

## Notes

- Keystore: `android/app/release-keystore.jks` (password: `agribrain123`)
- Package name: `com.example.agribrain_ai`
- Minification: Disabled for manual testing
