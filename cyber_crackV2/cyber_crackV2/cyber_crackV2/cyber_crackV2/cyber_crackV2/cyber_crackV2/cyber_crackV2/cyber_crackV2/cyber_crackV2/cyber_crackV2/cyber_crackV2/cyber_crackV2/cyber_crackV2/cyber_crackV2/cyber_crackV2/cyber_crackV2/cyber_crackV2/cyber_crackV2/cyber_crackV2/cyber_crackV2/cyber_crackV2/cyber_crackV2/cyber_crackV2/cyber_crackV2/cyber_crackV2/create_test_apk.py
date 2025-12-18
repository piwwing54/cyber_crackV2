#!/usr/bin/env python3
"""
🧪 CYBER CRACK PRO TEST - Create test APK with real Smali files
"""

import zipfile
import tempfile
from pathlib import Path

def create_test_apk_with_smali():
    """Create a test APK with actual Smali files to test method analysis"""
    
    # Create a temporary APK with Smali files for testing
    test_apk_path = Path("test_apk_with_smali.apk")
    
    with zipfile.ZipFile(test_apk_path, 'w') as apk_zip:
        # Add a minimal AndroidManifest.xml
        manifest_content = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.testapp"
    android:versionCode="1"
    android:versionName="1.0">
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <application android:label="Test App">
        <activity android:name=".MainActivity">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>'''
        apk_zip.writestr("AndroidManifest.xml", manifest_content.encode('utf-8'))
        
        # Add a dummy DEX file
        apk_zip.writestr("classes.dex", b"dex_file_content_for_testing")
        
        # Add a fake Smali file to test method analysis
        smali_content = '''# This is a fake Smali file for testing
.class public Lcom/example/testapp/SecurityCheck;
.super Ljava/lang/Object;

.method public static isRooted()Z
    .locals 1
    const/4 v0, 0x0
    return v0
.end method

.method public static isPurchased()Z
    .locals 1
    const/4 v0, 0x0
    return v0
.end method

.method public static checkLicense()Z
    .locals 1
    const/4 v0, 0x0
    return v0
.end method
'''
        apk_zip.writestr("smali/com/example/testapp/SecurityCheck.smali", smali_content.encode('utf-8'))
        
        # Add another Smali file
        main_activity_smali = '''# Main Activity Smali
.class public Lcom/example/testapp/MainActivity;
.super Landroid/app/Activity;

.method public onCreate(Landroid/os/Bundle;)V
    .locals 1
    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V
    return-void
.end method

.method private verifyPayment()Z
    .locals 1
    const/4 v0, 0x0
    return v0
.end method
'''
        apk_zip.writestr("smali/com/example/testapp/MainActivity.smali", main_activity_smali.encode('utf-8'))
    
    print(f"Test APK with Smali created: {test_apk_path}")
    return test_apk_path

if __name__ == "__main__":
    create_test_apk_with_smali()