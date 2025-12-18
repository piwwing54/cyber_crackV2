package com.cybercrack;

public class Main {
    public static void main(String[] args) {
        System.out.println("CyberCrack Java DEX Analyzer");
        
        if (args.length < 1) {
            System.out.println("Usage: java -jar JavaDexAnalyzer.jar <command> [options]");
            System.out.println("Commands:");
            System.out.println("  analyze <apk_path>     - Analyze APK for vulnerabilities");
            System.out.println("  crack <apk_path> <type> - Apply specific crack to APK");
            System.out.println("  patch <dex_path> <type> - Apply patch to DEX file");
            System.exit(1);
        }
        
        String command = args[0];
        
        switch (command) {
            case "analyze":
                if (args.length < 2) {
                    System.out.println("Usage: java -jar JavaDexAnalyzer.jar analyze <apk_path>");
                    System.exit(1);
                }
                analyzeAPK(args[1]);
                break;
                
            case "crack":
                if (args.length < 3) {
                    System.out.println("Usage: java -jar JavaDexAnalyzer.jar crack <apk_path> <type>");
                    System.out.println("Types: certificate_pinning, root_detection, iap_bypass, login_bypass");
                    System.exit(1);
                }
                crackAPK(args[1], args[2]);
                break;
                
            case "patch":
                if (args.length < 3) {
                    System.out.println("Usage: java -jar JavaDexAnalyzer.jar patch <dex_path> <type>");
                    System.out.println("Types: certificate_pinning, root_detection, iap_bypass");
                    System.exit(1);
                }
                patchDex(args[1], args[2]);
                break;
                
            default:
                System.out.println("Unknown command: " + command);
                System.out.println("Use: analyze, crack, or patch");
                System.exit(1);
        }
    }
    
    private static void analyzeAPK(String apkPath) {
        System.out.println("Analyzing APK: " + apkPath);
        
        // Create analyzer instance
        AndroidAnalyzer analyzer = new AndroidAnalyzer();
        
        // Perform analysis
        analyzer.analyze(apkPath);
    }
    
    private static void crackAPK(String apkPath, String crackType) {
        System.out.println("Cracking APK (" + crackType + "): " + apkPath);
        
        // Create cracker instance
        DexCracker cracker = new DexCracker();
        
        // Apply crack
        cracker.applyCrack(apkPath, crackType);
    }
    
    private static void patchDex(String dexPath, String patchType) {
        System.out.println("Patching DEX (" + patchType + "): " + dexPath);
        
        // Create smali patcher
        SmaliPatcher patcher = new SmaliPatcher();
        
        // Apply patch
        patcher.patch(dexPath, patchType);
    }
}