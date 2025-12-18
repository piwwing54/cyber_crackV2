package main

import (
	"archive/zip"
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"
)

// Decompiler handles APK decompilation
type Decompiler struct {
	ApkPath string
	OutputDir string
}

// NewDecompiler creates a new decompiler instance
func NewDecompiler(apkPath, outputDir string) *Decompiler {
	return &Decompiler{
		ApkPath:   apkPath,
		OutputDir: outputDir,
	}
}

// Decompile decompiles the APK to the output directory
func (d *Decompiler) Decompile() error {
	// Create output directory
	if err := os.MkdirAll(d.OutputDir, 0755); err != nil {
		return fmt.Errorf("failed to create output directory: %v", err)
	}
	
	// Extract APK
	if err := d.extractAPK(); err != nil {
		return fmt.Errorf("failed to extract APK: %v", err)
	}
	
	return nil
}

// extractAPK extracts the APK file
func (d *Decompiler) extractAPK() error {
	reader, err := zip.OpenReader(d.ApkPath)
	if err != nil {
		return fmt.Errorf("failed to open APK: %v", err)
	}
	defer reader.Close()
	
	for _, file := range reader.File {
		filePath := filepath.Join(d.OutputDir, file.Name)
		
		// Security check: prevent zip slip
		if !strings.HasPrefix(filePath, filepath.Clean(d.OutputDir)+string(os.PathSeparator)) {
			return fmt.Errorf("illegal file path: %s", filePath)
		}
		
		if file.FileInfo().IsDir() {
			// Create directory
			if err := os.MkdirAll(filePath, file.Mode()); err != nil {
				return fmt.Errorf("failed to create directory: %v", err)
			}
		} else {
			// Create parent directories if needed
			if err := os.MkdirAll(filepath.Dir(filePath), 0755); err != nil {
				return fmt.Errorf("failed to create parent directories: %v", err)
			}
			
			// Extract file
			if err := d.extractFile(file, filePath); err != nil {
				return fmt.Errorf("failed to extract file %s: %v", file.Name, err)
			}
		}
	}
	
	return nil
}

// extractFile extracts a single file from the APK
func (d *Decompiler) extractFile(zipFile *zip.File, filePath string) error {
	zipFileReader, err := zipFile.Open()
	if err != nil {
		return err
	}
	defer zipFileReader.Close()
	
	content, err := ioutil.ReadAll(zipFileReader)
	if err != nil {
		return err
	}
	
	return ioutil.WriteFile(filePath, content, 0644)
}

// GetSmaliFiles returns paths to all smali files in the decompiled APK
func (d *Decompiler) GetSmaliFiles() ([]string, error) {
	var smaliFiles []string
	
	err := filepath.Walk(d.OutputDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return nil // Continue walking despite errors
		}
		
		if !info.IsDir() && strings.HasSuffix(strings.ToLower(path), ".smali") {
			smaliFiles = append(smaliFiles, path)
		}
		
		return nil
	})
	
	if err != nil {
		return nil, err
	}
	
	return smaliFiles, nil
}

// GetManifestPath returns the path to AndroidManifest.xml
func (d *Decompiler) GetManifestPath() string {
	return filepath.Join(d.OutputDir, "AndroidManifest.xml")
}

// GetAssetPaths returns paths to all asset files
func (d *Decompiler) GetAssetPaths() ([]string, error) {
	var assetPaths []string
	
	assetsDir := filepath.Join(d.OutputDir, "assets")
	if _, err := os.Stat(assetsDir); os.IsNotExist(err) {
		return assetPaths, nil // No assets directory
	}
	
	err := filepath.Walk(assetsDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return nil // Continue despite errors
		}
		
		if !info.IsDir() {
			assetPaths = append(assetPaths, path)
		}
		
		return nil
	})
	
	return assetPaths, err
}