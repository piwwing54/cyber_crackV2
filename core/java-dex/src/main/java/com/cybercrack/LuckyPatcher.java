package com.cybercrack;

import java.io.*;
import java.util.*;
import java.util.regex.Pattern;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import java.util.zip.ZipOutputStream;
import java.nio.file.*;

/**
 * Additional patcher with Lucky Patcher-like functionality
 */
public class LuckyPatcher {

    public enum PatchType {
        REMOVE_ADS("remove_ads", "Remove advertisements"),
        REMOVE_LICENSE_CHECK("remove_license_check", "Remove license checks"),
        REMOVE_GOOGLE_LOGIN("remove_google_login", "Remove Google login requirements"),
        REMOVE_ROOT_DETECTION("remove_root_detection", "Remove root detection"),
        REMOVE_CERT_PINNING("remove_cert_pinning", "Remove certificate pinning"),
        UNLOCK_PREMIUM("unlock_premium", "Unlock premium features"),
        BYPASS_VERIFICATION("bypass_verification", "Bypass verification checks"),
        AGGRESSIVE_PATCHING("aggressive_patching", "Apply aggressive patches");

        private final String id;
        private final String description;

        PatchType(String id, String description) {
            this.id = id;
            this.description = description;
        }

        public String getId() { return id; }
        public String getDescription() { return description; }
    }

    /**
     * Apply Lucky Patcher-style patches to an APK
     */
    public static ApplyPatchesResult applyLuckyPatches(String apkPath, List<PatchType> patches) {
        ApplyPatchesResult result = new ApplyPatchesResult();
        result.setSuccess(true);
        result.setAppliedPatches(new ArrayList<>());
        result.setModifiedFiles(new ArrayList<>());

        if (patches.isEmpty()) {
            result.setMessage("No patches to apply");
            return result;
        }

        try {
            // Create temporary directory for extraction
            String tempDir = createTempDir("lucky_patcher_");
            String extractedPath = extractAPK(apkPath, tempDir);

            try {
                // Apply each patch
                for (PatchType patch : patches) {
                    switch (patch) {
                        case REMOVE_ADS:
                            List<String> adFiles = removeAds(extractedPath);
                            result.getModifiedFiles().addAll(adFiles);
                            result.getAppliedPatches().add("Removed ads from " + adFiles.size() + " files");
                            break;
                        case REMOVE_LICENSE_CHECK:
                            List<String> licenseFiles = removeLicenseCheck(extractedPath);
                            result.getModifiedFiles().addAll(licenseFiles);
                            result.getAppliedPatches().add("Removed license checks from " + licenseFiles.size() + " files");
                            break;
                        case REMOVE_GOOGLE_LOGIN:
                            List<String> loginFiles = removeGoogleLogin(extractedPath);
                            result.getModifiedFiles().addAll(loginFiles);
                            result.getAppliedPatches().add("Removed Google login from " + loginFiles.size() + " files");
                            break;
                        case REMOVE_ROOT_DETECTION:
                            List<String> rootFiles = removeRootDetection(extractedPath);
                            result.getModifiedFiles().addAll(rootFiles);
                            result.getAppliedPatches().add("Removed root detection from " + rootFiles.size() + " files");
                            break;
                        case REMOVE_CERT_PINNING:
                            List<String> certFiles = removeCertPinning(extractedPath);
                            result.getModifiedFiles().addAll(certFiles);
                            result.getAppliedPatches().add("Removed certificate pinning from " + certFiles.size() + " files");
                            break;
                        case UNLOCK_PREMIUM:
                            List<String> premiumFiles = unlockPremium(extractedPath);
                            result.getModifiedFiles().addAll(premiumFiles);
                            result.getAppliedPatches().add("Unlocked premium features in " + premiumFiles.size() + " files");
                            break;
                        case BYPASS_VERIFICATION:
                            List<String> verifyFiles = bypassVerification(extractedPath);
                            result.getModifiedFiles().addAll(verifyFiles);
                            result.getAppliedPatches().add("Applied verification bypasses to " + verifyFiles.size() + " files");
                            break;
                        case AGGRESSIVE_PATCHING:
                            List<String> aggressiveFiles = applyAggressivePatches(extractedPath);
                            result.getModifiedFiles().addAll(aggressiveFiles);
                            result.getAppliedPatches().add("Applied aggressive patches to " + aggressiveFiles.size() + " files");
                            break;
                    }
                }

                // Rebuild APK with patches applied
                String patchedApkPath = apkPath.replace(".apk", "_patched.apk");
                rebuildAPK(extractedPath, patchedApkPath);

                // Sign the patched APK
                try {
                    signAPK(patchedApkPath);
                    result.setPatchedApkPath(patchedApkPath);
                } catch (Exception e) {
                    System.err.println("Warning: Could not sign APK: " + e.getMessage());
                    result.setPatchedApkPath(patchedApkPath);
                    result.setSuccess(false);
                }

            } finally {
                // Clean up temporary directory
                cleanupTempDir(tempDir);
            }

        } catch (Exception e) {
            result.setSuccess(false);
            result.setError("Error applying patches: " + e.getMessage());
        }

        return result;
    }

    /**
     * Remove ads from APK
     */
    private static List<String> removeAds(String extractedPath) throws IOException {
        List<String> modifiedFiles = new ArrayList<>();
        
        // Look for common ad-related patterns and remove them
        Files.walk(Paths.get(extractedPath))
            .filter(Files::isRegularFile)
            .filter(path -> path.toString().endsWith(".smali") || path.toString().endsWith(".xml"))
            .forEach(path -> {
                try {
                    String content = new String(Files.readAllBytes(path));
                    String originalContent = content;

                    // Remove ad-related code patterns
                    content = content.replaceAll(
                        "(?i)(admob|AdMob|googleads|GoogleAds|unityads|UnityAds|chartboost|Chartboost)",
                        "StubAd"  // Replace with stub implementations
                    );
                    
                    content = content.replaceAll(
                        "(?i)(loadAd\\(\\)|showAd\\(\\)|requestAd\\(\\))",
                        "return true;"
                    );

                    // Check if content was modified
                    if (!content.equals(originalContent)) {
                        Files.write(path, content.getBytes());
                        modifiedFiles.add(path.toString());
                    }
                } catch (IOException e) {
                    System.err.println("Error processing file: " + path + " - " + e.getMessage());
                }
            });

        return modifiedFiles;
    }

    /**
     * Remove license check (Google Play licensing)
     */
    private static List<String> removeLicenseCheck(String extractedPath) throws IOException {
        List<String> modifiedFiles = new ArrayList<>();
        
        // Look for license check methods in smali files
        Path smaliDir = Paths.get(extractedPath, "smali");
        if (Files.exists(smaliDir)) {
            Files.walk(smaliDir)
                .filter(Files::isRegularFile)
                .filter(path -> path.toString().endsWith(".smali"))
                .forEach(path -> {
                    try {
                        String content = new String(Files.readAllBytes(path));
                        String originalContent = content;

                        // Patch license check methods to always return success
                        content = content.replaceAll(
                            "(const/4 v0, 0x0)",  // return false
                            "const/4 v0, 0x1"     // return true
                        );
                        
                        // Replace license check calls
                        content = content.replaceAll(
                            "(?i)(invoke.*checkLicense)",
                            "const/4 v0, 0x1\n    move-result v0"
                        );

                        // Check if content was modified
                        if (!content.equals(originalContent)) {
                            Files.write(path, content.getBytes());
                            modifiedFiles.add(path.toString());
                        }
                    } catch (IOException e) {
                        System.err.println("Error processing file: " + path + " - " + e.getMessage());
                    }
                });
        }

        return modifiedFiles;
    }

    /**
     * Remove Google login requirements
     */
    private static List<String> removeGoogleLogin(String extractedPath) throws IOException {
        List<String> modifiedFiles = new ArrayList<>();
        
        Files.walk(Paths.get(extractedPath))
            .filter(Files::isRegularFile)
            .filter(path -> path.toString().endsWith(".smali"))
            .forEach(path -> {
                try {
                    String content = new String(Files.readAllBytes(path));
                    String originalContent = content;

                    // Bypass Google login
                    content = content.replaceAll(
                        "(?i)(GoogleSignInOptions|GoogleSignInClient|GoogleSignIn)",
                        "StubSignIn"  // Replace with stub implementations
                    );
                    
                    content = content.replaceAll(
                        "(?i)(GoogleAuthUtil.getToken)",
                        "const-string v0, \"fake_token\"\n    return-object v0"
                    );

                    // Check if content was modified
                    if (!content.equals(originalContent)) {
                        Files.write(path, content.getBytes());
                        modifiedFiles.add(path.toString());
                    }
                } catch (IOException e) {
                    System.err.println("Error processing file: " + path + " - " + e.getMessage());
                }
            });

        return modifiedFiles;
    }

    /**
     * Remove root detection
     */
    private static List<String> removeRootDetection(String extractedPath) throws IOException {
        List<String> modifiedFiles = new ArrayList<>();
        
        Files.walk(Paths.get(extractedPath))
            .filter(Files::isRegularFile)
            .filter(path -> path.toString().endsWith(".smali"))
            .forEach(path -> {
                try {
                    String content = new String(Files.readAllBytes(path));
                    String originalContent = content;

                    // Bypass root detection by making checks always return false
                    content = content.replaceAll(
                        "(?i)(isRooted|checkRoot|rootPath|suBinary|isDeviceRooted)",
                        "const/4 v0, 0x0\n    return v0"  // Always return false (not rooted)
                    );
                    
                    // Change return values in root detection methods
                    content = content.replaceAll(
                        "(const/4 v0, 0x1)",  // return true
                        "const/4 v0, 0x0"     // return false
                    );

                    // Check if content was modified
                    if (!content.equals(originalContent)) {
                        Files.write(path, content.getBytes());
                        modifiedFiles.add(path.toString());
                    }
                } catch (IOException e) {
                    System.err.println("Error processing file: " + path + " - " + e.getMessage());
                }
            });

        return modifiedFiles;
    }

    /**
     * Remove certificate pinning
     */
    private static List<String> removeCertPinning(String extractedPath) throws IOException {
        List<String> modifiedFiles = new ArrayList<>();
        
        Files.walk(Paths.get(extractedPath))
            .filter(Files::isRegularFile)
            .filter(path -> path.toString().endsWith(".smali"))
            .forEach(path -> {
                try {
                    String content = new String(Files.readAllBytes(path));
                    String originalContent = content;

                    // Bypass certificate pinning
                    content = content.replaceAll(
                        "(?i)(checkServerTrusted|checkClientTrusted|pinCertificate)",
                        "new-instance v0, Ljava/security/cert/X509Certificate;\n    const/4 v1, 0x0\n    new-array v0, v1, [Ljava/security/cert/X509Certificate;\n    return-object v0"
                    );
                    
                    // Replace pinning methods with always-accept implementations
                    content = content.replaceAll(
                        "(?i)(PinningTrustManager|CertificatePinner)",
                        "AcceptAllTrustManager"
                    );

                    // Check if content was modified
                    if (!content.equals(originalContent)) {
                        Files.write(path, content.getBytes());
                        modifiedFiles.add(path.toString());
                    }
                } catch (IOException e) {
                    System.err.println("Error processing file: " + path + " - " + e.getMessage());
                }
            });

        return modifiedFiles;
    }

    /**
     * Unlock premium features
     */
    private static List<String> unlockPremium(String extractedPath) throws IOException {
        List<String> modifiedFiles = new ArrayList<>();
        
        Files.walk(Paths.get(extractedPath))
            .filter(Files::isRegularFile)
            .filter(path -> path.toString().endsWith(".smali"))
            .forEach(path -> {
                try {
                    String content = new String(Files.readAllBytes(path));
                    String originalContent = content;

                    // Unlock premium features by making checks always return true
                    content = content.replaceAll(
                        "(?i)(isPro|isPremium|isUnlocked|hasPaid|isSubscribed)",
                        "const/4 v0, 0x1\n    return v0"  // Always return true
                    );
                    
                    content = content.replaceAll(
                        "(?i)(hasFeature\\(\"premium\"\\))",
                        "const/4 v0, 0x1\n    return v0"
                    );
                    
                    // Change return values to unlock features
                    content = content.replaceAll(
                        "(const/4 v0, 0x0)",  // return false
                        "const/4 v0, 0x1"     // return true
                    );

                    // Check if content was modified
                    if (!content.equals(originalContent)) {
                        Files.write(path, content.getBytes());
                        modifiedFiles.add(path.toString());
                    }
                } catch (IOException e) {
                    System.err.println("Error processing file: " + path + " - " + e.getMessage());
                }
            });

        return modifiedFiles;
    }

    /**
     * Bypass various verification checks
     */
    private static List<String> bypassVerification(String extractedPath) throws IOException {
        List<String> modifiedFiles = new ArrayList<>();
        
        Files.walk(Paths.get(extractedPath))
            .filter(Files::isRegularFile)
            .filter(path -> path.toString().endsWith(".smali"))
            .forEach(path -> {
                try {
                    String content = new String(Files.readAllBytes(path));
                    String originalContent = content;

                    // Bypass common verification patterns
                    content = content.replaceAll(
                        "(?i)(verify|validate|check|authenticate)",
                        "stub"  // Change method names to stubs
                    );
                    
                    // Replace verification results with success
                    content = content.replaceAll(
                        "(?i)(if.*verify)",
                        "if (true) { // verify"  // Always pass verification
                    );

                    // Check if content was modified
                    if (!content.equals(originalContent)) {
                        Files.write(path, content.getBytes());
                        modifiedFiles.add(path.toString());
                    }
                } catch (IOException e) {
                    System.err.println("Error processing file: " + path + " - " + e.getMessage());
                }
            });

        return modifiedFiles;
    }

    /**
     * Apply aggressive patches
     */
    private static List<String> applyAggressivePatches(String extractedPath) throws IOException {
        List<String> modifiedFiles = new ArrayList<>();
        
        Files.walk(Paths.get(extractedPath))
            .filter(Files::isRegularFile)
            .filter(path -> path.toString().endsWith(".smali"))
            .forEach(path -> {
                try {
                    String content = new String(Files.readAllBytes(path));
                    String originalContent = content;

                    // Apply more aggressive patches
                    // Always return true for security checks
                    content = content.replaceAll(
                        "(const/4 v0, 0x0)",  // return false
                        "const/4 v0, 0x1"     // return true
                    );
                    
                    // Remove security exceptions
                    content = content.replaceAll(
                        "(?i)(SecurityException|security.check)",
                        "StubException"
                    );
                    
                    // Bypass integrity checks
                    content = content.replaceAll(
                        "(?i)(verifySignature|checkIntegrity)",
                        "const/4 v0, 0x1\n    return v0"
                    );

                    // Check if content was modified
                    if (!content.equals(originalContent)) {
                        Files.write(path, content.getBytes());
                        modifiedFiles.add(path.toString());
                    }
                } catch (IOException e) {
                    System.err.println("Error processing file: " + path + " - " + e.getMessage());
                }
            });

        return modifiedFiles;
    }

    /**
     * Extract APK to temporary directory
     */
    private static String extractAPK(String apkPath, String tempDir) throws IOException {
        File apkFile = new File(apkPath);
        ZipFile zipFile = new ZipFile(apkFile);

        java.util.Enumeration<? extends ZipEntry> entries = zipFile.entries();
        while (entries.hasMoreElements()) {
            ZipEntry entry = entries.nextElement();
            File entryDestination = new File(tempDir, entry.getName());

            if (entry.isDirectory()) {
                entryDestination.mkdirs();
            } else {
                entryDestination.getParentFile().mkdirs();
                try (InputStream in = zipFile.getInputStream(entry);
                     OutputStream out = new FileOutputStream(entryDestination)) {

                    byte[] buffer = new byte[1024];
                    int length;
                    while ((length = in.read(buffer)) >= 0) {
                        out.write(buffer, 0, length);
                    }
                }
            }
        }

        zipFile.close();
        return tempDir;
    }

    /**
     * Rebuild APK from extracted directory
     */
    private static void rebuildAPK(String extractedPath, String outputPath) throws IOException {
        File outputAPK = new File(outputPath);
        outputAPK.createNewFile();

        try (FileOutputStream fos = new FileOutputStream(outputAPK);
             ZipOutputStream zos = new ZipOutputStream(fos)) {

            Path extractedDir = Paths.get(extractedPath);
            Files.walk(extractedDir)
                .filter(path -> !path.toFile().isDirectory())
                .forEach(path -> {
                    try {
                        String entryName = extractedDir.relativize(path).toString();
                        ZipEntry zipEntry = new ZipEntry(entryName);
                        zos.putNextEntry(zipEntry);

                        Files.copy(path, zos);
                        zos.closeEntry();
                    } catch (IOException e) {
                        System.err.println("Error adding file to APK: " + e.getMessage());
                    }
                });
        }
    }

    /**
     * Sign the modified APK using the same method as in DEXCracker
     */
    private static void signAPK(String apkPath) throws IOException, InterruptedException {
        // This uses the same implementation as in DEXCracker.java
        // Ensure we have the keystore file
        String keystorePath = createDebugKeystoreIfNotExists();

        // Sign the APK using apksigner
        ProcessBuilder pb = new ProcessBuilder(
            "apksigner", "sign",
            "--ks", keystorePath,
            "--ks-key-alias", "androiddebugkey",
            "--ks-pass", "pass:android",
            "--key-pass", "pass:android",
            "--v4-signing-enabled", "false", // Disable v4 signing to ensure compatibility
            apkPath
        );
        
        // Set environment if needed
        pb.environment().put("PATH", pb.environment().get("PATH") + ":/android/sdk/build-tools/latest");
        
        Process process = pb.start();
        
        // Capture output for debugging
        String output = new BufferedReader(new InputStreamReader(process.getInputStream()))
            .lines().collect(java.util.stream.Collectors.joining("\n"));
        String error = new BufferedReader(new InputStreamReader(process.getErrorStream()))
            .lines().collect(java.util.stream.Collectors.joining("\n"));

        int exitCode = process.waitFor();
        
        if (exitCode != 0) {
            System.err.println("APK signing failed: " + error);
            System.out.println("APK signing output: " + output);
            
            // Fallback: try alternative signing method
            tryAlternativeSigning(apkPath);
        } else {
            System.out.println("APK signed successfully");
        }
    }

    /**
     * Create debug keystore if it doesn't exist
     */
    private static String createDebugKeystoreIfNotExists() throws IOException, InterruptedException {
        String keystorePath = System.getProperty("user.home") + "/.android/debug.keystore";
        File keystoreFile = new File(keystorePath);
        
        if (!keystoreFile.exists()) {
            keystoreFile.getParentFile().mkdirs();
            
            // Create debug keystore using keytool
            ProcessBuilder pb = new ProcessBuilder(
                "keytool", "-genkey", "-v", 
                "-keystore", keystorePath,
                "-alias", "androiddebugkey",
                "-storepass", "android",
                "-keypass", "android",
                "-keyalg", "RSA",
                "-keysize", "2048",
                "-validity", "10000",
                "-dname", "CN=Android Debug,O=Android,C=US"
            );
            
            Process process = pb.start();
            int exitCode = process.waitFor();
            
            if (exitCode != 0) {
                // If keytool fails, create a temporary debug keystore
                // as fallback - this would be in a real implementation
                System.err.println("Failed to create debug keystore, using fallback");
                // Create default keystore path
                keystorePath = "/tmp/debug.keystore";
                
                // Create debug keystore in /tmp
                ProcessBuilder pb2 = new ProcessBuilder(
                    "keytool", "-genkey", "-v", 
                    "-keystore", keystorePath,
                    "-alias", "androiddebugkey",
                    "-storepass", "android",
                    "-keypass", "android",
                    "-keyalg", "RSA",
                    "-keysize", "2048",
                    "-validity", "10000",
                    "-dname", "CN=Android Debug,O=Android,C=US"
                );
                
                Process process2 = pb2.start();
                int exitCode2 = process2.waitFor();
                
                if (exitCode2 != 0) {
                    throw new IOException("Failed to create debug keystore for signing");
                }
            }
        }
        
        return keystorePath;
    }

    /**
     * Alternative signing method using zipalign + signjar
     */
    private static void tryAlternativeSigning(String apkPath) throws IOException, InterruptedException {
        System.out.println("Trying alternative signing method...");
        
        // First align the APK
        String alignedApkPath = apkPath.replace(".apk", "_aligned.apk");
        
        // Try using zipalign if available
        ProcessBuilder zipalignPb = new ProcessBuilder(
            "zipalign", "-v", "-p", "4", apkPath, alignedApkPath
        );
        
        Process zipalignProc = zipalignPb.start();
        int zipalignExit = zipalignProc.waitFor();
        
        if (zipalignExit == 0) {
            // Use apksigner with aligned APK
            String keystorePath = createDebugKeystoreIfNotExists();
            
            ProcessBuilder pb = new ProcessBuilder(
                "apksigner", "sign", 
                "--ks", keystorePath,
                "--ks-key-alias", "androiddebugkey",
                "--ks-pass", "pass:android",
                "--key-pass", "pass:android",
                "--v4-signing-enabled", "false", // Disable v4 signing to ensure compatibility
                alignedApkPath
            );
            
            Process process = pb.start();
            int exitCode = process.waitFor();
            
            if (exitCode == 0) {
                // Replace original APK with signed one
                Files.move(Paths.get(alignedApkPath), Paths.get(apkPath), 
                          StandardCopyOption.REPLACE_EXISTING);
                System.out.println("APK signed successfully with alternative method");
                return;
            }
        }
        
        // If all methods fail, throw exception
        throw new IOException("All signing methods failed");
    }

    /**
     * Create temporary directory
     */
    private static String createTempDir(String prefix) throws IOException {
        File tempDir = File.createTempFile(prefix, "");
        tempDir.delete(); // Delete the file to make room for the directory
        tempDir.mkdir();
        return tempDir.getAbsolutePath();
    }

    /**
     * Clean up temporary directory
     */
    private static void cleanupTempDir(String tempDirPath) {
        File tempDir = new File(tempDirPath);
        deleteRecursively(tempDir);
    }

    /**
     * Delete directory recursively
     */
    private static void deleteRecursively(File file) {
        if (file.isDirectory()) {
            File[] children = file.listFiles();
            if (children != null) {
                for (File child : children) {
                    deleteRecursively(child);
                }
            }
        }
        file.delete();
    }
}

/**
 * Result class for patching operations
 */
class ApplyPatchesResult {
    private boolean success;
    private String error;
    private String message;
    private List<String> appliedPatches;
    private List<String> modifiedFiles;
    private String patchedApkPath;

    public ApplyPatchesResult() {
        this.appliedPatches = new ArrayList<>();
        this.modifiedFiles = new ArrayList<>();
    }

    // Getters and setters
    public boolean isSuccess() { return success; }
    public void setSuccess(boolean success) { this.success = success; }

    public String getError() { return error; }
    public void setError(String error) { this.error = error; }

    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }

    public List<String> getAppliedPatches() { return appliedPatches; }
    public void setAppliedPatches(List<String> appliedPatches) { this.appliedPatches = appliedPatches; }

    public List<String> getModifiedFiles() { return modifiedFiles; }
    public void setModifiedFiles(List<String> modifiedFiles) { this.modifiedFiles = modifiedFiles; }

    public String getPatchedApkPath() { return patchedApkPath; }
    public void setPatchedApkPath(String patchedApkPath) { this.patchedApkPath = patchedApkPath; }
}