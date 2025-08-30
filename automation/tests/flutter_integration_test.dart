import 'dart:io';
import 'dart:typed_data';
import 'dart:math';
import 'dart:convert';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:auto_job_apply/main.dart' as app;
import 'package:flutter/material.dart';

class TestUserManager {
  static String? _testEmail;
  static String? _testPassword;
  static String? _superUserEmail;
  static String? _superUserPassword;

  static String get testEmail => _testEmail ??= generateRandomEmail();
  static String get testPassword => _testPassword ??= 'TestPass123!';
  static String get superUserEmail =>
      _superUserEmail ??= 'admin@autojobapply.com';
  static String get superUserPassword =>
      _superUserPassword ??= 'SuperAdmin123!';

  static String generateRandomEmail() {
    final random = Random();
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    final randomNum = random.nextInt(9999);
    return 'autotest${timestamp}_$randomNum@gmail.com';
  }

  static Map<String, String> getTestCredentials() {
    return {
      'test_user_email': testEmail,
      'test_user_password': testPassword,
      'super_user_email': superUserEmail,
      'super_user_password': superUserPassword,
    };
  }
}

class ScreenshotHelper {
  static Future<void> takeScreenshot(
    WidgetTester tester,
    String screenName, {
    String? suffix,
    String? description,
  }) async {
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    final fileName = suffix != null
        ? '${screenName}_${suffix}_$timestamp.png'
        : '${screenName}_$timestamp.png';

    // Create directory if it doesn't exist
    final directory = Directory('automation/screenshots/$screenName');
    if (!directory.existsSync()) {
      directory.createSync(recursive: true);
    }

    // Take screenshot
    final Uint8List screenshot = await tester.binding.takeScreenshot(fileName);
    final File file = File('automation/screenshots/$screenName/$fileName');
    await file.writeAsBytes(screenshot);

    // Save metadata
    final metadataFile = File(
      'automation/screenshots/$screenName/${fileName.replaceAll('.png', '_metadata.json')}',
    );
    final metadata = {
      'screen_name': screenName,
      'suffix': suffix,
      'description': description ?? 'Screenshot of $screenName',
      'timestamp': DateTime.now().toIso8601String(),
      'file_name': fileName,
      'test_user': TestUserManager.testEmail,
      'screen_size':
          '${tester.view.physicalSize.width}x${tester.view.physicalSize.height}',
    };
    await metadataFile.writeAsString(jsonEncode(metadata));

    print('📸 Screenshot saved: ${file.path}');
    print('📋 Metadata saved: ${metadataFile.path}');
  }

  static Future<void> waitForScreenToLoad(WidgetTester tester) async {
    // Wait for animations and loading to complete
    await tester.pumpAndSettle(const Duration(seconds: 3));
    await Future.delayed(const Duration(milliseconds: 1000));
  }

  static Future<void> waitForNetworkRequest(WidgetTester tester) async {
    // Wait for network requests to complete
    await tester.pumpAndSettle(const Duration(seconds: 5));
    await Future.delayed(const Duration(milliseconds: 2000));
  }
}

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Auto Job Apply - Complete UI Automation Tests', () {
    testWidgets('Login Screen - UI and Functionality Test', (tester) async {
      // Start the app
      app.main();
      await tester.pumpAndSettle();

      // Wait for login screen to load
      await ScreenshotHelper.waitForScreenToLoad(tester);

      // Take initial screenshot
      await ScreenshotHelper.takeScreenshot(
        tester,
        'login_screen',
        suffix: 'initial',
      );

      // Verify login screen elements
      expect(find.text('Welcome Back'), findsOneWidget);
      expect(find.text('Sign in to your account'), findsOneWidget);
      expect(
        find.byType(TextField),
        findsAtLeast(2),
      ); // Email and password fields
      expect(find.text('Sign In'), findsOneWidget);
      expect(find.text('Sign in with Google'), findsOneWidget);
      expect(find.text('Sign in with Microsoft'), findsOneWidget);

      // Test email input
      final emailField = find.byKey(const Key('email_field'));
      await tester.enterText(emailField, 'test@automation.com');
      await tester.pumpAndSettle();

      // Test password input
      final passwordField = find.byKey(const Key('password_field'));
      await tester.enterText(passwordField, 'testpassword123');
      await tester.pumpAndSettle();

      // Take screenshot with filled form
      await ScreenshotHelper.takeScreenshot(
        tester,
        'login_screen',
        suffix: 'filled_form',
      );

      // Test form validation
      final signInButton = find.text('Sign In');
      await tester.tap(signInButton);
      await tester.pumpAndSettle();

      // Take screenshot after form submission
      await ScreenshotHelper.takeScreenshot(
        tester,
        'login_screen',
        suffix: 'after_submit',
      );
    });

    testWidgets('Dashboard Screen - Navigation and UI Test', (tester) async {
      // Assuming we're logged in, test dashboard
      app.main();
      await tester.pumpAndSettle();

      // Navigate to dashboard (mock login success)
      // This would typically involve mocking the auth state

      await ScreenshotHelper.waitForScreenToLoad(tester);
      await ScreenshotHelper.takeScreenshot(
        tester,
        'dashboard',
        suffix: 'main_view',
      );

      // Test navigation drawer
      final drawerButton = find.byIcon(Icons.menu);
      if (drawerButton.evaluate().isNotEmpty) {
        await tester.tap(drawerButton);
        await tester.pumpAndSettle();
        await ScreenshotHelper.takeScreenshot(
          tester,
          'dashboard',
          suffix: 'drawer_open',
        );
      }
    });

    testWidgets('Job Application Screen - Form and Functionality', (
      tester,
    ) async {
      app.main();
      await tester.pumpAndSettle();

      // Navigate to job application screen
      // This would involve navigation logic

      await ScreenshotHelper.waitForScreenToLoad(tester);
      await ScreenshotHelper.takeScreenshot(
        tester,
        'job_application',
        suffix: 'form_view',
      );

      // Test form fields
      final jobTitleField = find.byKey(const Key('job_title_field'));
      if (jobTitleField.evaluate().isNotEmpty) {
        await tester.enterText(jobTitleField, 'Software Engineer');
        await tester.pumpAndSettle();
      }

      final companyField = find.byKey(const Key('company_field'));
      if (companyField.evaluate().isNotEmpty) {
        await tester.enterText(companyField, 'Tech Company Inc.');
        await tester.pumpAndSettle();
      }

      await ScreenshotHelper.takeScreenshot(
        tester,
        'job_application',
        suffix: 'filled_form',
      );
    });

    testWidgets('Resume Upload Screen - File Handling Test', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Navigate to resume upload screen

      await ScreenshotHelper.waitForScreenToLoad(tester);
      await ScreenshotHelper.takeScreenshot(
        tester,
        'resume_upload',
        suffix: 'initial_view',
      );

      // Test file upload button
      final uploadButton = find.byKey(const Key('upload_resume_button'));
      if (uploadButton.evaluate().isNotEmpty) {
        await tester.tap(uploadButton);
        await tester.pumpAndSettle();
        await ScreenshotHelper.takeScreenshot(
          tester,
          'resume_upload',
          suffix: 'upload_dialog',
        );
      }
    });

    testWidgets('Settings Screen - Configuration Test', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Navigate to settings screen

      await ScreenshotHelper.waitForScreenToLoad(tester);
      await ScreenshotHelper.takeScreenshot(
        tester,
        'settings',
        suffix: 'main_view',
      );

      // Test theme toggle
      final themeToggle = find.byKey(const Key('theme_toggle'));
      if (themeToggle.evaluate().isNotEmpty) {
        await tester.tap(themeToggle);
        await tester.pumpAndSettle();
        await ScreenshotHelper.takeScreenshot(
          tester,
          'settings',
          suffix: 'dark_theme',
        );
      }
    });

    testWidgets('Responsive Design Test - Different Screen Sizes', (
      tester,
    ) async {
      app.main();
      await tester.pumpAndSettle();

      // Test mobile size
      await tester.binding.setSurfaceSize(const Size(375, 667)); // iPhone SE
      await tester.pumpAndSettle();
      await ScreenshotHelper.takeScreenshot(
        tester,
        'responsive',
        suffix: 'mobile_375',
      );

      // Test tablet size
      await tester.binding.setSurfaceSize(const Size(768, 1024)); // iPad
      await tester.pumpAndSettle();
      await ScreenshotHelper.takeScreenshot(
        tester,
        'responsive',
        suffix: 'tablet_768',
      );

      // Test desktop size
      await tester.binding.setSurfaceSize(const Size(1920, 1080)); // Desktop
      await tester.pumpAndSettle();
      await ScreenshotHelper.takeScreenshot(
        tester,
        'responsive',
        suffix: 'desktop_1920',
      );

      // Reset to default size
      await tester.binding.setSurfaceSize(null);
    });

    testWidgets('Accessibility Test - Screen Reader and Navigation', (
      tester,
    ) async {
      app.main();
      await tester.pumpAndSettle();

      await ScreenshotHelper.waitForScreenToLoad(tester);

      // Test semantic labels
      expect(find.bySemanticsLabel('Email input field'), findsWidgets);
      expect(find.bySemanticsLabel('Password input field'), findsWidgets);
      expect(find.bySemanticsLabel('Sign in button'), findsWidgets);

      // Test keyboard navigation
      await tester.sendKeyEvent(LogicalKeyboardKey.tab);
      await tester.pumpAndSettle();

      await ScreenshotHelper.takeScreenshot(
        tester,
        'accessibility',
        suffix: 'keyboard_focus',
      );
    });
  });
}
