# Flutter Integration Guide for TT Cyclopedia Backend

## Overview

This document describes how to connect Flutter clients (mobile/web/desktop) to the TT Cyclopedia FastAPI backend.

---

## 1. Connection URLs by Platform

Flutter apps use different addresses to reach the backend depending on the platform:

| Platform | Backend URL | Notes |
|----------|-------------|-------|
| **React Frontend (Web)** | `http://localhost:8000` | Same machine |
| **Flutter Web** | `http://localhost:8000` | Same machine |
| **iOS Simulator** | `http://localhost:8000` | iOS simulator shares host network |
| **Android Emulator** | `http://10.0.2.2:8000` | Special alias for host localhost |
| **Real Device (same WiFi)** | `http://<host-ip>:8000` | Use your computer's local IP |
| **Production** | `https://api.ttcyclopedia.space` | HTTPS required |

### Finding Your Host IP (for real devices)

```bash
# macOS/Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows
ipconfig
```

Example: `http://192.168.1.45:8000`

---

## 2. CORS Configuration

### 2.1 Native Mobile Apps (iOS/Android/Desktop)

**Good news:** Native mobile apps do NOT enforce CORS. CORS is a browser security feature only. As long as the device can reach the backend IP, requests will work.

No backend CORS changes needed for native Flutter apps.

### 2.2 Flutter Web

Flutter Web runs in a browser, so CORS applies. The backend must allow the Flutter web origin.

**Current CORS origins in `.env`:**
```env
ALLOWED_ORIGINS=https://ttcyclopedia.space,http://localhost:3000,http://localhost:5173
```

**Add Flutter Web origin:**
```env
# For Flutter web development (default port 8080 or 3000)
ALLOWED_ORIGINS=https://ttcyclopedia.space,http://localhost:3000,http://localhost:5173,http://localhost:8080
```

If using a custom port for Flutter web, add it to the list.

### 2.3 Production

For production, ensure CORS allows:
```env
ALLOWED_ORIGINS=https://ttcyclopedia.space,https://your-flutter-app-domain.com
```

---

## 3. Backend Changes Required

### 3.1 Allow All Origins for Development (Optional)

If you want to accept connections from any origin during development, modify `app/main.py`:

```python
# For development only - allows any origin
if os.getenv("ENVIRONMENT", "development") == "development":
    ALLOWED_ORIGINS = ["*"]
else:
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "https://ttcyclopedia.space").split(",")
```

**Warning:** Never use `["*"]` with `allow_credentials=True` in production.

### 3.2 Bind to All Interfaces

The backend must bind to `0.0.0.0` (not just `127.0.0.1`) to accept connections from other devices:

```bash
# Current (good)
uvicorn app.main:app --host 0.0.0.0 --port 8000

# This allows connections from:
# - localhost (127.0.0.1)
# - 10.0.2.2 (Android emulator)
# - 192.168.x.x (local network devices)
```

The backend is already configured this way.

### 3.3 Network Access (macOS Firewall)

On macOS, you may need to allow Python through the firewall:
- System Settings → Network → Firewall → Allow Python

---

## 4. Flutter HTTP Client Setup

### 4.1 Recommended: Dio Package

```yaml
# pubspec.yaml
dependencies:
  dio: ^5.8.0+1
  flutter_dotenv: ^5.2.1
```

```dart
// lib/config/api_config.dart
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

class ApiConfig {
  static String get baseUrl {
    if (kIsWeb) {
      // Flutter Web
      return 'http://localhost:8000';
    }
    
    #if ANDROID
      // Android Emulator
      return 'http://10.0.2.2:8000';
    #elif IOS
      // iOS Simulator
      return 'http://localhost:8000';
    #else
      // Desktop or other
      return 'http://localhost:8000';
    #endif
    
    // For real devices, use your computer's IP:
    // return 'http://192.168.1.45:8000';
  }
  
  static Dio get dio {
    final dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
      headers: {
        'Content-Type': 'application/json',
      },
    ));
    
    // Add auth interceptor
    dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        // Add JWT token if available
        final token = getToken(); // Your token storage
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
      onError: (error, handler) {
        // Handle 401 - token expired
        if (error.response?.statusCode == 401) {
          clearToken();
          // Navigate to login
        }
        return handler.next(error);
      },
    ));
    
    return dio;
  }
}

// Simple token storage (replace with secure storage for production)
String? _token;
String? getToken() => _token;
void setToken(String token) => _token = token;
void clearToken() => _token = null;
```

### 4.2 Using HTTP Package (Built-in)

```yaml
# pubspec.yaml
dependencies:
  http: ^1.2.0
```

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io' show Platform;

String getBaseUrl() {
  if (kIsWeb) return 'http://localhost:8000';
  if (Platform.isAndroid) return 'http://10.0.2.2:8000';
  if (Platform.isIOS) return 'http://localhost:8000';
  return 'http://localhost:8000';
}

// GET posts
Future<List<dynamic>> fetchPosts() async {
  final response = await http.get(Uri.parse('${getBaseUrl()}/posts'));
  if (response.statusCode == 200) {
    return jsonDecode(response.body);
  }
  throw Exception('Failed to load posts');
}

// POST login
Future<Map<String, dynamic>> login(String username, String password) async {
  final response = await http.post(
    Uri.parse('${getBaseUrl()}/users/login'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({'username': username, 'password': password}),
  );
  if (response.statusCode == 200) {
    return jsonDecode(response.body);
  }
  throw Exception('Login failed');
}

// POST with auth
Future<void> likePost(String postId, String token) async {
  final response = await http.post(
    Uri.parse('${getBaseUrl()}/posts/$postId/toggle-like'),
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    },
  );
  if (response.statusCode != 200) {
    throw Exception('Like failed');
  }
}
```

---

## 5. Android-Specific Configuration

### 5.1 AndroidManifest.xml

Add internet permission and allow cleartext (HTTP) traffic for local development:

```xml
<!-- android/app/src/main/AndroidManifest.xml -->
<manifest ...>
    <!-- Internet permission -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    
    <application
        ...
        android:usesCleartextTraffic="true"> <!-- Allow HTTP (dev only) -->
        ...
    </application>
</manifest>
```

**Remove `android:usesCleartextTraffic="true"` for production!**

### 5.2 Network Security Config (Production)

For production with HTTPS:
```xml
<!-- android/app/src/main/res/xml/network_security_config.xml -->
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.ttcyclopedia.space</domain>
    </domain-config>
</network-security-config>
```

```xml
<!-- AndroidManifest.xml -->
<application
    android:networkSecurityConfig="@xml/network_security_config">
```

---

## 6. iOS-Specific Configuration

### 6.1 Info.plist (for localhost/HTTP)

iOS blocks HTTP by default (ATS). Add exception for local development:

```xml
<!-- ios/Runner/Info.plist -->
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <false/>
    <key>NSExceptionDomains</key>
    <dict>
        <key>localhost</key>
        <dict>
            <key>NSExceptionAllowsInsecureHTTPLoads</key>
            <true/>
            <key>NSIncludesSubdomains</key>
            <true/>
        </dict>
        <!-- For real device testing with IP -->
        <key>192.168.1.45</key>
        <dict>
            <key>NSExceptionAllowsInsecureHTTPLoads</key>
            <true/>
        </dict>
    </dict>
</dict>
```

**Remove exceptions for production!**

---

## 7. Testing the Connection

### 7.1 Test Backend is Reachable

```dart
Future<void> testConnection() async {
  try {
    final response = await http.get(Uri.parse('${ApiConfig.baseUrl}/health'));
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      print('Backend connected: ${data['status']}');
    }
  } catch (e) {
    print('Connection failed: $e');
  }
}
```

### 7.2 Test Login

```dart
Future<void> testLogin() async {
  try {
    final response = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/users/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': 'demo_user',
        'password': 'demo123456',
      }),
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final token = data['access_token'];
      setToken(token);
      print('Login successful, token: $token');
    } else {
      print('Login failed: ${response.body}');
    }
  } catch (e) {
    print('Login error: $e');
  }
}
```

---

## 8. Production Setup

### 8.1 Environment Variables

Create a `.env` file for Flutter:

```env
# .env (for flutter_dotenv package)
API_BASE_URL=https://api.ttcyclopedia.space
DEFAULT_IMAGE_URL=https://api.ttcyclopedia.space/static/default/default.jpeg
```

### 8.2 HTTPS Only

Production MUST use HTTPS. Configure the backend with SSL:

```env
# backend .env
ENABLE_HTTPS_REDIRECT=true
ENABLE_HSTS=true
DATABASE_SSL=true
```

### 8.3 CORS for Production

```env
# backend .env
ALLOWED_ORIGINS=https://ttcyclopedia.space,https://your-flutter-app.com
```

---

## 9. Quick Start Checklist

For a Flutter developer connecting to this backend:

- [ ] Backend running: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- [ ] Backend health check: `curl http://localhost:8000/health`
- [ ] Backend CORS includes Flutter origin (if web)
- [ ] Android: `usesCleartextTraffic="true"` in manifest (dev only)
- [ ] iOS: `NSExceptionAllowsInsecureHTTPLoads` for localhost in Info.plist (dev only)
- [ ] Flutter base URL correct for platform:
  - Android Emulator: `http://10.0.2.2:8000`
  - iOS Simulator: `http://localhost:8000`
  - Real Device: `http://<your-ip>:8000`
- [ ] Test user created: `demo_user` / `demo123456`
- [ ] Token stored and sent with `Authorization: Bearer <token>`

---

## 10. Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `Connection refused` | Backend not running | Start backend: `uvicorn app.main:app --host 0.0.0.0 --port 8000` |
| `Connection refused` (Android) | Wrong IP | Use `10.0.2.2:8000` for emulator |
| `Connection refused` (real device) | Different network | Connect device to same WiFi, use host IP |
| `CORS Missing Allow Origin` | Flutter Web | Add `http://localhost:8080` to `ALLOWED_ORIGINS` |
| `401 Unauthorized` | No/missing token | Login first, send `Authorization: Bearer <token>` |
| `403 Forbidden` | Invalid token | Re-login to get fresh token |
| `Cleartext HTTP traffic not permitted` (Android) | HTTPS enforcement | Add `usesCleartextTraffic="true"` |
| `The resource could not be loaded` (iOS) | ATS blocking | Add localhost exception to `Info.plist` |

---

## 11. API Endpoints Summary

### Auth
```
POST /users/login          → {access_token, token_type, user}
POST /users                → Create user
GET  /auth/validate        → Validate token (needs Bearer)
```

### Posts
```
GET    /posts              → List posts (optional ?search=)
GET    /posts/{id}         → Get single post
POST   /posts              → Create post (multipart/form-data)
DELETE /posts/{id}         → Delete own post
POST   /posts/{id}/toggle-like → Like/unlike
```

### Forums
```
GET    /forums             → List forums
GET    /forums/{id}        → Get forum
POST   /forums             → Create forum
PUT    /forums/{id}        → Update forum
DELETE /forums/{id}        → Delete forum
POST   /forums/{id}/toggle-like → Like/unlike
```

### Comments
```
GET    /comments/post/{post_id}        → Post comments
POST   /comments                       → Create comment
PUT    /comments/{id}                 → Update comment
DELETE /comments/{id}                 → Delete comment
POST   /comments/{id}/toggle-like     → Like/unlike
```

### Users
```
GET    /users              → List users
GET    /users/{id}         → Get user
DELETE /users/{id}         → Delete own account
```

---

**Last Updated:** 2025-05-03
**Backend Version:** 0.1.0
**Required Headers:** `Content-Type: application/json`, `Authorization: Bearer <token>` (for protected routes)
