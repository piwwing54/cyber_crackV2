package main

import (
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

// PatternScanner scans files for specific patterns
type PatternScanner struct {
	ApkPath string
}

// NewPatternScanner creates a new pattern scanner instance
func NewPatternScanner(apkPath string) *PatternScanner {
	return &PatternScanner{ApkPath: apkPath}
}

// ScanForPatterns scans the APK for various security patterns
func (ps *PatternScanner) ScanForPatterns() (*AnalysisResult, error) {
	// Create a temporary directory for extracted APK
	tempDir, err := ioutil.TempDir("", "apk_analysis_")
	if err != nil {
		return nil, fmt.Errorf("failed to create temp directory: %v", err)
	}
	defer os.RemoveAll(tempDir)
	
	// Decompile APK to temp directory
	decompiler := NewDecompiler(ps.ApkPath, tempDir)
	if err := decompiler.Decompile(); err != nil {
		return nil, fmt.Errorf("failed to decompile APK: %v", err)
	}
	
	result := &AnalysisResult{
		Vulnerabilities: []Vulnerability{},
		Protections:     []string{},
		Recommendations: []string{},
		Success:         true,
	}
	
	// Scan different parts of the APK
	if err := ps.scanManifest(tempDir, result); err != nil {
		return nil, fmt.Errorf("failed to scan manifest: %v", err)
	}
	
	if err := ps.scanSmaliFiles(tempDir, result); err != nil {
		return nil, fmt.Errorf("failed to scan smali files: %v", err)
	}
	
	if err := ps.scanAssetFiles(tempDir, result); err != nil {
		return nil, fmt.Errorf("failed to scan asset files: %v", err)
	}
	
	// Calculate security score
	result.SecurityScore = calculateSecurityScore(result.Vulnerabilities, result.Protections)
	result.EnginesUsed = 1
	
	return result, nil
}

// scanManifest scans AndroidManifest.xml for security issues
func (ps *PatternScanner) scanManifest(dirPath string, result *AnalysisResult) error {
	manifestPath := filepath.Join(dirPath, "AndroidManifest.xml")
	
	content, err := ioutil.ReadFile(manifestPath)
	if err != nil {
		// If manifest doesn't exist, we can't scan it
		return nil
	}
	
	contentStr := string(content)
	
	// Define patterns for security issues in manifest
	securityPatterns := []struct {
		pattern     *regexp.Regexp
		vulnType    string
		severity    string
		description string
		recommendation string
	}{
		{
			pattern:     regexp.MustCompile(`(?i)allowBackup="true"`),
			vulnType:    "Backup Allowed",
			severity:    "MEDIUM",
			description: "App allows backup which may expose sensitive data",
			recommendation: "Set allowBackup=\"false\" in AndroidManifest.xml",
		},
		{
			pattern:     regexp.MustCompile(`(?i)usesCleartextTraffic="true"`),
			vulnType:    "Cleartext Traffic Allowed",
			severity:    "HIGH",
			description: "App allows cleartext traffic which is insecure",
			recommendation: "Set usesCleartextTraffic=\"false\" in AndroidManifest.xml",
		},
		{
			pattern:     regexp.MustCompile(`(?i)android:exported="true"`),
			vulnType:    "Component Exported",
			severity:    "MEDIUM",
			description: "App component exported without proper protection",
			recommendation: "Set android:exported=\"false\" or add proper permission",
		},
		{
			pattern:     regexp.MustCompile(`(?i)android:debuggable="true"`),
			vulnType:    "Debug Enabled",
			severity:    "HIGH",
			description: "App is debuggable which is insecure in production",
			recommendation: "Set android:debuggable=\"false\" in production builds",
		},
	}
	
	for _, secPattern := range securityPatterns {
		if secPattern.pattern.MatchString(contentStr) {
			// Find all matches to report them separately
			matches := secPattern.pattern.FindAllString(contentStr, -1)
			for _, match := range matches {
				result.Vulnerabilities = append(result.Vulnerabilities, Vulnerability{
					Type:          secPattern.vulnType,
					Severity:      secPattern.severity,
					Description:   fmt.Sprintf("%s: Found %s in manifest", secPattern.description, match),
					Recommendation: secPattern.recommendation,
				})
			}
		}
	}
	
	return nil
}

// scanSmaliFiles scans all smali files for security patterns
func (ps *PatternScanner) scanSmaliFiles(dirPath string, result *AnalysisResult) error {
	smaliDir := filepath.Join(dirPath, "smali")
	
	// Walk through smali directory
	err := filepath.Walk(smaliDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return nil // Continue despite errors
		}
		
		if !info.IsDir() && strings.HasSuffix(strings.ToLower(path), ".smali") {
			if err := ps.scanSmaliFile(path, result); err != nil {
				// Log error but continue scanning other files
				fmt.Printf("Error scanning smali file %s: %v\n", path, err)
			}
		}
		
		return nil
	})
	
	return err
}

// scanSmaliFile scans a single smali file for security patterns
func (ps *PatternScanner) scanSmaliFile(filePath string, result *AnalysisResult) error {
	content, err := ioutil.ReadFile(filePath)
	if err != nil {
		return fmt.Errorf("failed to read file: %v", err)
	}
	
	contentStr := string(content)
	
	// Define patterns for vulnerabilities in smali code
	vulnerabilityPatterns := []struct {
		pattern     *regexp.Regexp
		vulnType    string
		severity    string
		description string
		recommendation string
	}{
		{
			pattern:     regexp.MustCompile(`(?i)(const-string.*password|const-string.*secret|const-string.*token|const-string.*api_key)`),
			vulnType:    "Hardcoded Credential",
			severity:    "CRITICAL",
			description: "Hardcoded credential found in code",
			recommendation: "Use secure storage for credentials",
		},
		{
			pattern:     regexp.MustCompile(`(?i)(invoke.*login|invoke.*authenticate|invoke.*auth)`),
			vulnType:    "Authentication Check",
			severity:    "INFO",
			description: "Authentication method call found",
			recommendation: "Review authentication implementation",
		},
		{
			pattern:     regexp.MustCompile(`(?i)(if-eqz.*auth|if-nez.*auth)`),
			vulnType:    "Authentication Bypass",
			severity:    "HIGH",
			description: "Potential authentication bypass condition found",
			recommendation: "Ensure proper authentication checks",
		},
		{
			pattern:     regexp.MustCompile(`(?i)(const-string.*http://)`),
			vulnType:    "HTTP URL",
			severity:    "HIGH",
			description: "HTTP URL found, traffic is unencrypted",
			recommendation: "Use HTTPS for all network requests",
		},
		{
			pattern:     regexp.MustCompile(`(?i)(openFileOutput|getSharedPreferences)`),
			vulnType:    "Insecure Storage",
			severity:    "HIGH",
			description: "Potentially insecure storage method used",
			recommendation: "Use encrypted storage for sensitive data",
		},
		{
			pattern:     regexp.MustCompile(`(?i)(cipher.getInstance\(".*MD5|cipher.getInstance\(".*DES|cipher.getInstance\(".*RC4)`),
			vulnType:    "Weak Cryptography",
			severity:    "HIGH",
			description: "Weak cryptographic algorithm used",
			recommendation: "Use strong cryptographic algorithms (AES-256, RSA-2048+)",
		},
	}
	
	// Define patterns for protections in smali code
	protectionPatterns := []struct {
		pattern *regexp.Regexp
		name    string
	}{
		{
			pattern: regexp.MustCompile(`(?i)(checkServerTrusted|X509TrustManager|SSLSocketFactory)`),
			name:    "Certificate Pinning",
		},
		{
			pattern: regexp.MustCompile(`(?i)(isRooted|rootbeer|root check|superuser)`),
			name:    "Root Detection",
		},
		{
			pattern: regexp.MustCompile(`(?i)(isDebuggerConnected|debugger|jdwp)`),
			name:    "Anti-Debug",
		},
		{
			pattern: regexp.MustCompile(`(?i)(getSignature|packageManager|signature)`),
			name:    "Signature Verification",
		},
		{
			pattern: regexp.MustCompile(`(?i)(getApplicationInfo|packageName|package name)`),
			name:    "Package Verification",
		},
		{
			pattern: regexp.MustCompile(`(?i)(obfuscate|proguard|reflection)`),
			name:    "Code Obfuscation",
		},
	}
	
	// Scan for vulnerabilities
	for _, vulnPattern := range vulnerabilityPatterns {
		if vulnPattern.pattern.MatchString(contentStr) {
			// Find all matches to report them separately
			matches := vulnPattern.pattern.FindAllString(contentStr, -1)
			for _, match := range matches {
				result.Vulnerabilities = append(result.Vulnerabilities, Vulnerability{
					Type:          vulnPattern.vulnType,
					Severity:      vulnPattern.severity,
					Description:   fmt.Sprintf("%s: Found %s in %s", vulnPattern.description, match, filePath),
					Recommendation: vulnPattern.recommendation,
				})
			}
		}
	}
	
	// Scan for protections
	for _, protPattern := range protectionPatterns {
		if protPattern.pattern.MatchString(contentStr) {
			// Extract the specific protection mechanism
			matches := protPattern.pattern.FindAllString(contentStr, -1)
			for _, match := range matches {
				// Only add unique protections
				if !containsString(result.Protections, protPattern.name) {
					result.Protections = append(result.Protections, protPattern.name)
				}
			}
		}
	}
	
	return nil
}

// scanAssetFiles scans asset files for sensitive information
func (ps *PatternScanner) scanAssetFiles(dirPath string, result *AnalysisResult) error {
	assetsDir := filepath.Join(dirPath, "assets")
	
	if _, err := os.Stat(assetsDir); os.IsNotExist(err) {
		return nil // No assets to scan
	}
	
	// Walk through assets directory
	err := filepath.Walk(assetsDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return nil // Continue despite errors
		}
		
		if !info.IsDir() && isTextFile(path) {
			if err := ps.scanAssetFile(path, result); err != nil {
				// Log error but continue scanning other files
				fmt.Printf("Error scanning asset file %s: %v\n", path, err)
			}
		}
		
		return nil
	})
	
	return err
}

// scanAssetFile scans a single asset file for sensitive information
func (ps *PatternScanner) scanAssetFile(filePath string, result *AnalysisResult) error {
	content, err := ioutil.ReadFile(filePath)
	if err != nil {
		return fmt.Errorf("failed to read file: %v", err)
	}
	
	contentStr := string(content)
	
	// Define patterns for sensitive info in asset files
	sensitivePatterns := []struct {
		pattern     *regexp.Regexp
		vulnType    string
		severity    string
		description string
		recommendation string
	}{
		{
			pattern:     regexp.MustCompile(`(?i)("password":|"secret":|"token":|"api_key":)\s*"([^"]{5,})"`),
			vulnType:    "Hardcoded Credential in Asset",
			severity:    "CRITICAL",
			description: "Hardcoded credential found in asset file",
			recommendation: "Remove credentials from asset files",
		},
		{
			pattern:     regexp.MustCompile(`(?i)(http://[^\s")]+)`),
			vulnType:    "HTTP Endpoint in Asset",
			severity:    "HIGH",
			description: "HTTP endpoint found in asset file",
			recommendation: "Use HTTPS endpoints",
		},
		{
			pattern:     regexp.MustCompile(`(?i)(ftp://|smb://)`),
			vulnType:    "Insecure Protocol in Asset",
			severity:    "HIGH",
			description: "Insecure protocol found in asset file",
			recommendation: "Use secure protocols (HTTPS, SFTP)",
		},
	}
	
	for _, sensPattern := range sensitivePatterns {
		if sensPattern.pattern.MatchString(contentStr) {
			matches := sensPattern.pattern.FindAllString(contentStr, -1)
			for _, match := range matches {
				result.Vulnerabilities = append(result.Vulnerabilities, Vulnerability{
					Type:          sensPattern.vulnType,
					Severity:      sensPattern.severity,
					Description:   fmt.Sprintf("%s: Found %s in %s", sensPattern.description, match, filePath),
					Recommendation: sensPattern.recommendation,
				})
			}
		}
	}
	
	return nil
}

// containsString checks if a string slice contains a specific string
func containsString(slice []string, s string) bool {
	for _, item := range slice {
		if item == s {
			return true
		}
	}
	return false
}

// Helper function to check if file is text file (imported from analyzer.go)
func isTextFile(filePath string) bool {
	ext := strings.ToLower(filepath.Ext(filePath))
	textExts := []string{".txt", ".java", ".smali", ".xml", ".json", ".js", ".html", ".css", ".py", ".cpp", ".c", ".h", ".go", ".rs"}
	
	for _, te := range textExts {
		if ext == te {
			return true
		}
	}
	
	return false
}