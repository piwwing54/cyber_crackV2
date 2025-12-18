package main

import (
	"bufio"
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"
)

// Analyzer handles APK analysis
type Analyzer struct {
	ApkPath string
}

// NewAnalyzer creates a new analyzer instance
func NewAnalyzer(apkPath string) *Analyzer {
	return &Analyzer{ApkPath: apkPath}
}

// Analyze performs comprehensive APK analysis
func (a *Analyzer) Analyze() (*AnalysisResult, error) {
	result := &AnalysisResult{
		Vulnerabilities: []Vulnerability{},
		Protections:     []string{},
		Recommendations: []string{},
		Success:         true,
	}
	
	// Perform various analyses
	if err := a.analyzeManifest(result); err != nil {
		return nil, fmt.Errorf("manifest analysis failed: %v", err)
	}
	
	if err := a.analyzeAssets(result); err != nil {
		return nil, fmt.Errorf("assets analysis failed: %v", err)
	}
	
	if err := a.analyzeCode(result); err != nil {
		return nil, fmt.Errorf("code analysis failed: %v", err)
	}
	
	// Calculate security score
	result.SecurityScore = calculateSecurityScore(result.Vulnerabilities, result.Protections)
	result.EnginesUsed = 1
	
	return result, nil
}

// analyzeManifest analyzes AndroidManifest.xml
func (a *Analyzer) analyzeManifest(result *AnalysisResult) error {
	manifestPath := filepath.Join(filepath.Dir(a.ApkPath), "AndroidManifest.xml")
	
	// In a real implementation, we'd parse the manifest file
	// For now we'll simulate by checking if file exists and contains common issues
	content, err := ioutil.ReadFile(manifestPath)
	if err != nil {
		// If manifest doesn't exist in extracted form, create dummy analysis
		// This is a simplified version - real analysis would parse XML
		result.Vulnerabilities = append(result.Vulnerabilities, Vulnerability{
			Type:          "Missing Manifest Analysis",
			Severity:      "INFO",
			Description:   "AndroidManifest.xml not found in expected location",
			Recommendation: "Verify APK structure",
		})
		return nil
	}
	
	contentStr := string(content)
	
	// Check for potential vulnerabilities in manifest
	if strings.Contains(strings.ToLower(contentStr), "allowbackup=\"true\"") {
		result.Vulnerabilities = append(result.Vulnerabilities, Vulnerability{
			Type:          "Backup Allowed",
			Severity:      "MEDIUM",
			Description:   "App allows backup which may expose sensitive data",
			Recommendation: "Set allowBackup=\"false\" in AndroidManifest.xml",
		})
	}
	
	if strings.Contains(strings.ToLower(contentStr), "usesCleartextTraffic=\"true\"") {
		result.Vulnerabilities = append(result.Vulnerabilities, Vulnerability{
			Type:          "Cleartext Traffic Allowed",
			Severity:      "HIGH",
			Description:   "App allows cleartext traffic which is insecure",
			Recommendation: "Set usesCleartextTraffic=\"false\" in AndroidManifest.xml",
		})
	}
	
	return nil
}

// analyzeAssets analyzes assets in the APK
func (a *Analyzer) analyzeAssets(result *AnalysisResult) error {
	assetsDir := filepath.Join(filepath.Dir(a.ApkPath), "assets")
	
	// Check if assets directory exists
	if _, err := os.Stat(assetsDir); os.IsNotExist(err) {
		return nil // No assets to analyze
	}
	
	// Walk through assets directory
	err := filepath.Walk(assetsDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return nil // Skip problematic files
		}
		
		if !info.IsDir() && isTextFile(path) {
			// Check for sensitive information in asset files
			content, err := ioutil.ReadFile(path)
			if err != nil {
				return nil // Skip unreadable files
			}
			
			// Look for hardcoded credentials in assets
			if containsSensitiveInfo(string(content)) {
				result.Vulnerabilities = append(result.Vulnerabilities, Vulnerability{
					Type:          "Hardcoded Credentials in Assets",
					Severity:      "CRITICAL",
					Description:   fmt.Sprintf("Sensitive information found in asset file: %s", path),
					Recommendation: "Remove hardcoded credentials from asset files",
				})
			}
		}
		
		return nil
	})
	
	return err
}

// analyzeCode analyzes code files (smali, java, etc.)
func (a *Analyzer) analyzeCode(result *AnalysisResult) error {
	codeDir := filepath.Join(filepath.Dir(a.ApkPath), "smali")
	
	// Check if code directory exists
	if _, err := os.Stat(codeDir); os.IsNotExist(err) {
		return nil // No code to analyze
	}
	
	// Walk through code directory
	err := filepath.Walk(codeDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return nil // Skip problematic files
		}
		
		if !info.IsDir() && isTextFile(path) {
			// Analyze code file for vulnerabilities
			fileVulns, fileProtections := analyzeCodeFile(path)
			result.Vulnerabilities = append(result.Vulnerabilities, fileVulns...)
			result.Protections = append(result.Protections, fileProtections...)
		}
		
		return nil
	})
	
	return err
}

// analyzeCodeFile analyzes a single code file
func analyzeCodeFile(filePath string) ([]Vulnerability, []string) {
	vulns := []Vulnerability{}
	protections := []string{}
	
	content, err := ioutil.ReadFile(filePath)
	if err != nil {
		return vulns, protections
	}
	
	contentStr := string(content)
	
	// Look for common vulnerability patterns in code
	scanner := bufio.NewScanner(strings.NewReader(contentStr))
	lineNum := 0
	
	for scanner.Scan() {
		lineNum++
		line := scanner.Text()
		lineLower := strings.ToLower(line)
		
		// Check for hardcoded credentials
		if containsSensitivePattern(lineLower) {
			vulns = append(vulns, Vulnerability{
				Type:          "Hardcoded Credential",
				Severity:      "CRITICAL",
				Description:   fmt.Sprintf("Potential hardcoded credential found in %s:%d - %s", filePath, lineNum, line),
				Recommendation: "Use secure storage for credentials",
			})
		}
		
		// Check for weak cryptography
		if containsWeakCrypto(lineLower) {
			vulns = append(vulns, Vulnerability{
				Type:          "Weak Cryptography",
				Severity:      "HIGH",
				Description:   fmt.Sprintf("Weak cryptography detected in %s:%d - %s", filePath, lineNum, line),
				Recommendation: "Use strong cryptographic algorithms",
			})
		}
		
		// Check for insecure storage
		if containsInsecureStorage(lineLower) {
			vulns = append(vulns, Vulnerability{
				Type:          "Insecure Storage",
				Severity:      "HIGH",
				Description:   fmt.Sprintf("Insecure storage detected in %s:%d - %s", filePath, lineNum, line),
				Recommendation: "Use secure storage mechanisms",
			})
		}
		
		// Check for protections
		if containsProtection(lineLower) {
			protectionName := extractProtectionName(lineLower)
			protections = append(protections, protectionName)
		}
	}
	
	return vulns, protections
}

// containsSensitiveInfo checks if content contains sensitive information
func containsSensitiveInfo(content string) bool {
	sensitivePatterns := []string{
		"password",
		"secret",
		"token",
		"api_key",
		"auth",
		"key:",
		"pwd",
		"credential",
	}
	
	contentLower := strings.ToLower(content)
	
	for _, pattern := range sensitivePatterns {
		if strings.Contains(contentLower, pattern) {
			// Additional check to avoid false positives
			if !isCommonWordUsage(contentLower, pattern) {
				return true
			}
		}
	}
	
	return false
}

// containsSensitivePattern checks for sensitive patterns in a line
func containsSensitivePattern(line string) bool {
	patterns := []string{
		"password",
		"secret",
		"token",
		"api_key",
		"auth",
		"key =",
		"pwd",
		"credential",
		"\".*[0-9A-Za-z]{20,}",
	}
	
	for _, pattern := range patterns {
		if strings.Contains(line, pattern) {
			return true
		}
	}
	
	return false
}

// containsWeakCrypto checks for weak cryptographic implementations
func containsWeakCrypto(line string) bool {
	weakCryptoPatterns := []string{
		"md5",
		"des",
		"rc4",
		"base64",
		"simplecrypt",
		"weakhash",
	}
	
	for _, pattern := range weakCryptoPatterns {
		if strings.Contains(line, pattern) {
			return true
		}
	}
	
	return false
}

// containsInsecureStorage checks for insecure storage usage
func containsInsecureStorage(line string) bool {
	insecureStoragePatterns := []string{
		"sharedpreferences",
		"getfilesdir",
		"getcachedir",
		"openfileoutput",
		"sqlitedatabase",
		"contentresolver",
	}
	
	for _, pattern := range insecureStoragePatterns {
		if strings.Contains(line, pattern) {
			return true
		}
	}
	
	return false
}

// containsProtection checks for protection mechanisms
func containsProtection(line string) bool {
	protectionPatterns := []string{
		"certificatepinning",
		"trustmanager",
		"hostnameverifier",
		"root",
		"debug",
		"obfuscate",
		"proguard",
		"signature",
		"tamper",
	}
	
	for _, pattern := range protectionPatterns {
		if strings.Contains(line, pattern) {
			return true
		}
	}
	
	return false
}

// extractProtectionName extracts the name of the protection
func extractProtectionName(line string) string {
	// This is a simplified extraction - in reality you'd have more complex logic
	if strings.Contains(line, "certificatepinning") {
		return "Certificate Pinning"
	} else if strings.Contains(line, "root") {
		return "Root Detection"
	} else if strings.Contains(line, "debug") {
		return "Anti-Debug"
	} else if strings.Contains(line, "obfuscate") || strings.Contains(line, "proguard") {
		return "Code Obfuscation"
	} else if strings.Contains(line, "signature") {
		return "Signature Verification"
	} else if strings.Contains(line, "tamper") {
		return "Tamper Detection"
	}
	
	return "Protection Mechanism"
}

// isCommonWordUsage checks if a sensitive word is used in a non-sensitive context
func isCommonWordUsage(content, word string) bool {
	// This is a simplified check - in reality you'd have more sophisticated context analysis
	// For example, "password" in "password_reset" might be less sensitive than in "password = \"value\""
	
	// Common non-sensitive contexts
	nonSensitiveContexts := []string{
		"reset",
		"change",
		"forgot",
		"hint",
	}
	
	contentLower := strings.ToLower(content)
	
	for _, context := range nonSensitiveContexts {
		if strings.Contains(contentLower, word) && strings.Contains(contentLower, context) {
			return true
		}
	}
	
	return false
}