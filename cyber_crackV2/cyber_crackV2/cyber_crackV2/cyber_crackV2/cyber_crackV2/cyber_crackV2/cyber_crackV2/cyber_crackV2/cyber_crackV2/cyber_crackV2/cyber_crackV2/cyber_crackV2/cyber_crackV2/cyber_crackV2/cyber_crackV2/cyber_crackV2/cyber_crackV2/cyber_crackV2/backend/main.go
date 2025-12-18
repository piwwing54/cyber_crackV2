package main

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"sync"
	"time"

	"github.com/gorilla/mux"
	"github.com/gorilla/websocket"
	"github.com/rs/cors"
)

// APK Analysis Request
type APKRequest struct {
	ID          string    `json:"id"`
	Filename    string    `json:"filename"`
	OriginalURL string    `json:"original_url"`
	UploadTime  time.Time `json:"upload_time"`
	Status      string    `json:"status"`
	Progress    int       `json:"progress"`
}

// Crack Configuration
type CrackConfig struct {
	BypassLogin         bool `json:"bypass_login"`
	UnlockIAP           bool `json:"unlock_iap"`
	GameMods            bool `json:"game_mods"`
	PremiumUnlock       bool `json:"premium_unlock"`
	SecurityBypass      bool `json:"security_bypass"`
	LicenseCrack        bool `json:"license_crack"`
	SystemModifications bool `json:"system_modifications"`
	NetworkBypass       bool `json:"network_bypass"`
	PerformanceBoost    bool `json:"performance_boost"`
	AIEnhancedCrack     bool `json:"ai_enhanced_crack"`
	RemoveAds           bool `json:"remove_ads"`           // New: Remove ads functionality
	AggressivePatching  bool `json:"aggressive_patching"`  // New: Apply aggressive patches
}

// Global variables
var (
	uploadDir     = "./storage/uploads"
	processedDir  = "./storage/processed"
	tempDir       = "./storage/temp"
	requests      = make(map[string]*APKRequest)
	requestMutex  = &sync.RWMutex{}
	upgrader      = websocket.Upgrader{}
	maxUploadSize = int64(500 * 1024 * 1024) // 500MB
)

func main() {
	// Create directories
	os.MkdirAll(uploadDir, 0755)
	os.MkdirAll(processedDir, 0755)
	os.MkdirAll(tempDir, 0755)

	// Initialize router
	r := mux.NewRouter()

	// API Routes
	r.HandleFunc("/api/upload", uploadHandler).Methods("POST")
	r.HandleFunc("/api/analyze/{id}", analyzeHandler).Methods("POST")
	r.HandleFunc("/api/crack/{id}", crackHandler).Methods("POST")
	r.HandleFunc("/api/status/{id}", statusHandler).Methods("GET")
	r.HandleFunc("/api/download/{id}", downloadHandler).Methods("GET")
	r.HandleFunc("/api/queue", queueHandler).Methods("GET")
	r.HandleFunc("/ws/{id}", websocketHandler).Methods("GET")
	r.HandleFunc("/api/admin/stats", adminStatsHandler).Methods("GET")

	// Serve frontend
	r.PathPrefix("/").Handler(http.FileServer(http.Dir("./frontend/")))

	// CORS configuration
	c := cors.New(cors.Options{
		AllowedOrigins:   []string{"*"},
		AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowedHeaders:   []string{"Content-Type", "Authorization"},
		AllowCredentials: true,
	})

	// Start server
	handler := c.Handler(r)
	port := ":8080"
	log.Printf("🚀 Cyber Crack Pro Web Server starting on port %s", port)
	log.Fatal(http.ListenAndServe(port, handler))
}

// Upload handler
func uploadHandler(w http.ResponseWriter, r *http.Request) {
	// Validate file size
	r.Body = http.MaxBytesReader(w, r.Body, maxUploadSize)
	if err := r.ParseMultipartForm(maxUploadSize); err != nil {
		http.Error(w, "File too large (max 500MB)", http.StatusBadRequest)
		return
	}

	// Get file
	file, header, err := r.FormFile("apk")
	if err != nil {
		http.Error(w, "Invalid file", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// Generate unique ID
	id := generateID(header.Filename)
	filename := fmt.Sprintf("%s_%s", id, header.Filename)
	filepath := filepath.Join(uploadDir, filename)

	// Save file
	dst, err := os.Create(filepath)
	if err != nil {
		http.Error(w, "Failed to save file", http.StatusInternalServerError)
		return
	}
	defer dst.Close()

	if _, err := io.Copy(dst, file); err != nil {
		http.Error(w, "Failed to save file", http.StatusInternalServerError)
		return
	}

	// Create request record
	req := &APKRequest{
		ID:         id,
		Filename:   filename,
		UploadTime: time.Now(),
		Status:     "uploaded",
		Progress:   0,
	}

	requestMutex.Lock()
	requests[id] = req
	requestMutex.Unlock()

	// Return response
	response := map[string]interface{}{
		"id":       id,
		"filename": header.Filename,
		"size":     header.Size,
		"status":   "uploaded",
		"next_step": map[string]string{
			"analyze": fmt.Sprintf("/api/analyze/%s", id),
			"ws":      fmt.Sprintf("/ws/%s", id),
		},
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

// Analysis handler
func analyzeHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id := vars["id"]

	requestMutex.RLock()
	req, exists := requests[id]
	requestMutex.RUnlock()

	if !exists {
		http.Error(w, "Request not found", http.StatusNotFound)
		return
	}

	// Update status
	req.Status = "analyzing"
	req.Progress = 10

	// Start analysis in goroutine
	go func() {
		analyzeAPK(req)
	}()

	response := map[string]interface{}{
		"id":     id,
		"status": "analysis_started",
		"ws":     fmt.Sprintf("/ws/%s", id),
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

// Crack handler
func crackHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id := vars["id"]

	var config CrackConfig
	if err := json.NewDecoder(r.Body).Decode(&config); err != nil {
		http.Error(w, "Invalid configuration", http.StatusBadRequest)
		return
	}

	requestMutex.RLock()
	req, exists := requests[id]
	requestMutex.RUnlock()

	if !exists {
		http.Error(w, "Request not found", http.StatusNotFound)
		return
	}

	// Update status
	req.Status = "cracking"
	req.Progress = 30

	// Start cracking in goroutine
	go func() {
		crackAPK(req, config)
	}()

	response := map[string]interface{}{
		"id":     id,
		"status": "cracking_started",
		"config": config,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

// Status handler
func statusHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id := vars["id"]

	requestMutex.RLock()
	req, exists := requests[id]
	requestMutex.RUnlock()

	if !exists {
		http.Error(w, "Request not found", http.StatusNotFound)
		return
	}

	response := map[string]interface{}{
		"id":       req.ID,
		"filename": req.Filename,
		"status":   req.Status,
		"progress": req.Progress,
		"uploaded": req.UploadTime,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

// Download handler
func downloadHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id := vars["id"]

	requestMutex.RLock()
	req, exists := requests[id]
	requestMutex.RUnlock()

	if !exists || req.Status != "completed" {
		http.Error(w, "File not ready", http.StatusNotFound)
		return
	}

	// Find modified package file - support multiple formats
	supportedExtensions := []string{".apk", ".apks", ".xapk"}
	var filePath string
	var found bool

	for _, ext := range supportedExtensions {
		pattern := filepath.Join(processedDir, fmt.Sprintf("%s_*%s", id, ext))
		matches, err := filepath.Glob(pattern)
		if err == nil && len(matches) > 0 {
			filePath = matches[0]
			found = true
			break
		}
	}

	if !found {
		http.Error(w, "File not found", http.StatusNotFound)
		return
	}

	filename := filepath.Base(filePath)

	// Set appropriate content type based on file extension
	contentType := "application/octet-stream" // default
	if strings.HasSuffix(filename, ".apk") {
		contentType = "application/vnd.android.package-archive"
	} else if strings.HasSuffix(filename, ".apks") {
		contentType = "application/octet-stream" // APKS doesn't have a standard MIME type
	} else if strings.HasSuffix(filename, ".xapk") {
		contentType = "application/octet-stream" // XAPK doesn't have a standard MIME type
	}

	w.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=\"%s\"", filename))
	w.Header().Set("Content-Type", contentType)
	http.ServeFile(w, r, filePath)
}

// WebSocket handler
func websocketHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id := vars["id"]

	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println("WebSocket upgrade failed:", err)
		return
	}
	defer conn.Close()

	// Send real-time updates
	for {
		requestMutex.RLock()
		req, exists := requests[id]
		requestMutex.RUnlock()

		if !exists {
			conn.WriteMessage(websocket.TextMessage, []byte(`{"error": "Request not found"}`))
			break
		}

		update := map[string]interface{}{
			"id":       req.ID,
			"status":   req.Status,
			"progress": req.Progress,
			"time":     time.Now().Unix(),
		}

		message, _ := json.Marshal(update)
		if err := conn.WriteMessage(websocket.TextMessage, message); err != nil {
			break
		}

		if req.Status == "completed" || req.Status == "failed" {
			break
		}

		time.Sleep(1 * time.Second)
	}
}

// Queue handler
func queueHandler(w http.ResponseWriter, r *http.Request) {
	requestMutex.RLock()
	defer requestMutex.RUnlock()

	queue := make([]map[string]interface{}, 0)
	for id, req := range requests {
		queue = append(queue, map[string]interface{}{
			"id":       id,
			"filename": req.Filename,
			"status":   req.Status,
			"progress": req.Progress,
			"uploaded": req.UploadTime,
		})
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(queue)
}

// Admin stats handler
func adminStatsHandler(w http.ResponseWriter, r *http.Request) {
	requestMutex.RLock()
	defer requestMutex.RUnlock()

	// Count statuses
	statuses := make(map[string]int)
	for _, req := range requests {
		statuses[req.Status]++
	}

	// Calculate success rate
	total := len(requests)
	completed := statuses["completed"]
	successRate := 0.0
	if total > 0 {
		successRate = float64(completed) / float64(total) * 100
	}

	response := map[string]interface{}{
		"total_cracks":   total,
		"success_rate":   fmt.Sprintf("%.1f", successRate),
		"active_workers": 4, // This would be dynamic in real implementation
		"statuses":       statuses,
		"uptime":         time.Since(time.Now()).String(),
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

// Generate unique ID
func generateID(filename string) string {
	hash := sha256.New()
	hash.Write([]byte(filename + time.Now().String()))
	return hex.EncodeToString(hash.Sum(nil))[:16]
}

// Analyze APK function
func analyzeAPK(req *APKRequest) {
	// Set a timeout for the analysis process to prevent hanging
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Minute)
	defer cancel()

	req.Progress = 20

	// Call Python analyzer
	cmd := exec.CommandContext(ctx, "python3", "./core/python-bridge/bridge.py",
		"analyze",
		"--id", req.ID,
		"--file", filepath.Join(uploadDir, req.Filename),
		"--output", filepath.Join(tempDir, req.ID))

	output, err := cmd.CombinedOutput()

	// Check if the command timed out
	if ctx.Err() == context.DeadlineExceeded {
		req.Status = "analysis_timeout"
		req.Progress = 40
		log.Printf("❌ Analysis timed out for %s after 2 minutes", req.ID)
		return
	}

	if err != nil {
		req.Status = "analysis_failed"
		log.Printf("Analysis failed: %s", output)
		return
	}

	req.Progress = 40
	req.Status = "analyzed"
	log.Printf("Analysis completed for %s", req.ID)
}

// Crack APK function
func crackAPK(req *APKRequest, config CrackConfig) {
	// Set a timeout for the cracking process to prevent hanging
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Minute)
	defer cancel()

	req.Progress = 50

	// Prepare config file - include all new project_AI features
	configFile := filepath.Join(tempDir, fmt.Sprintf("%s_config.json", req.ID))

	// Prepare enhanced config with project_AI features
	enhancedConfig := map[string]interface{}{
		"bypass_login":         config.BypassLogin,
		"unlock_iap":           config.UnlockIAP,
		"game_mods":            config.GameMods,
		"premium_unlock":       config.PremiumUnlock,
		"security_bypass":      config.SecurityBypass,
		"license_crack":        config.LicenseCrack,
		"system_modifications": config.SystemModifications,
		"network_bypass":       config.NetworkBypass,
		"performance_boost":    config.PerformanceBoost,
		"ai_enhanced_crack":    config.AIEnhancedCrack,
		"remove_ads":           config.RemoveAds,           // New: Remove ads feature
		"aggressive_patching":  config.AggressivePatching,  // New: Aggressive patching feature
	}

	configJSON, _ := json.Marshal(enhancedConfig)
	os.WriteFile(configFile, configJSON, 0644)

	// Call enhanced Python crack engine with Super Gila Engine
	cmd := exec.CommandContext(ctx, "python3", "./core/python-bridge/bridge.py",
		"crack",
		"--id", req.ID,
		"--input", filepath.Join(uploadDir, req.Filename),
		"--config", configFile,
		"--output", processedDir)

	log.Printf("🚀 Starting SUPER GILA CRACK for: %s", req.Filename)
	log.Printf("🔧 Features enabled: %+v", enhancedConfig)

	output, err := cmd.CombinedOutput()

	// Check if the command timed out
	if ctx.Err() == context.DeadlineExceeded {
		req.Status = "cracking_timeout"
		req.Progress = 100
		log.Printf("❌ Cracking timed out for %s after 5 minutes", req.ID)
		return
	}

	if err != nil {
		req.Status = "cracking_failed"
		log.Printf("❌ Cracking failed: %s", output)
		log.Printf("⚠️  Error details: %v", err)

		// Check for specific error types to provide more detailed status
		outputStr := string(output)
		if strings.Contains(outputStr, "APKAnalyzer") || strings.Contains(outputStr, "analysis") {
			req.Status = "analysis_error"
		} else if strings.Contains(outputStr, "injection") || strings.Contains(outputStr, "patch") {
			req.Status = "injection_error"
		} else if strings.Contains(outputStr, "timeout") {
			req.Status = "cracking_timeout"
		}

		return
	}

	req.Progress = 80

	// Test stability
	go testStability(req)
}

// Test stability
func testStability(req *APKRequest) {
	// Set a timeout for the stability test to prevent hanging
	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Minute)
	defer cancel()

	cmd := exec.CommandContext(ctx, "python3", "./core/python-bridge/bridge.py",
		"test",
		"--id", req.ID,
		"--file", filepath.Join(processedDir, fmt.Sprintf("%s_cracked.apk", req.ID)))

	output, err := cmd.CombinedOutput()

	// Check if the command timed out
	if ctx.Err() == context.DeadlineExceeded {
		req.Status = "testing_timeout"
		req.Progress = 100
		log.Printf("❌ Stability test timed out for %s after 1 minute", req.ID)
		return
	}

	if err != nil {
		log.Printf("Stability test failed: %s", output)
		req.Status = "testing_failed"
		return
	}

	req.Progress = 100
	req.Status = "completed"
	log.Printf("Cracking completed for %s", req.ID)
}