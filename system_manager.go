package main

import (
	"fmt"
	"os"
	"os/exec"
	"strings"
	"time"
	"net/http"
	"log"
	"strconv"
	"sync"
	
	"github.com/gin-gonic/gin"
)

type SystemManager struct {
	services map[string]*Service
	mutex    sync.Mutex
}

type Service struct {
	Name        string
	PID         int
	Command     string
	Args        []string
	Status      string // running, stopped, error
	Port        int
	URL         string
	StartTime   time.Time
	LastCheck   time.Time
}

func NewSystemManager() *SystemManager {
	return &SystemManager{
		services: make(map[string]*Service),
	}
}

func (sm *SystemManager) StartService(name, command string, args ...string) error {
	sm.mutex.Lock()
	defer sm.mutex.Unlock()
	
	// Check if service is already running
	if svc, exists := sm.services[name]; exists && svc.Status == "running" {
		return fmt.Errorf("Service %s is already running", name)
	}
	
	cmd := exec.Command(command, args...)
	err := cmd.Start()
	if err != nil {
		return fmt.Errorf("Failed to start %s: %v", name, err)
	}
	
	service := &Service{
		Name:      name,
		PID:       cmd.Process.Pid,
		Command:   command,
		Args:      args,
		Status:    "running",
		StartTime: time.Now(),
		LastCheck: time.Now(),
	}
	
	sm.services[name] = service
	fmt.Printf("🚀 Started %s with PID: %d\n", name, cmd.Process.Pid)
	return nil
}

func (sm *SystemManager) StopService(name string) error {
	sm.mutex.Lock()
	defer sm.mutex.Unlock()
	
	service, exists := sm.services[name]
	if !exists {
		return fmt.Errorf("Service %s does not exist", name)
	}
	
	if service.Status != "running" {
		return fmt.Errorf("Service %s is not running", name)
	}
	
	cmd := exec.Command("kill", strconv.Itoa(service.PID))
	err := cmd.Run()
	if err != nil {
		return fmt.Errorf("Failed to stop %s (PID %d): %v", name, service.PID, err)
	}
	
	service.Status = "stopped"
	fmt.Printf("🛑 Stopped %s (PID: %d)\n", name, service.PID)
	return nil
}

func (sm *SystemManager) CheckStatus(name string) string {
	sm.mutex.Lock()
	defer sm.mutex.Unlock()
	
	service, exists := sm.services[name]
	if !exists {
		return "not_found"
	}
	
	// Coba cek apakah proses masih berjalan
	cmd := exec.Command("ps", "-p", strconv.Itoa(service.PID))
	err := cmd.Run()
	if err != nil {
		service.Status = "stopped"
		return service.Status
	}
	
	// Coba ping URL jika tersedia
	if service.URL != "" {
		client := http.Client{Timeout: 5 * time.Second}
		resp, err := client.Get(service.URL)
		if err == nil && resp.StatusCode == 200 {
			service.Status = "running"
		} else {
			service.Status = "unresponsive"
		}
		if resp != nil {
			resp.Body.Close()
		}
	} else {
		service.Status = "running"
	}
	service.LastCheck = time.Now()
	
	return service.Status
}

// Health endpoint handler
func (sm *SystemManager) getAllStatus(c *gin.Context) {
	status := make(map[string]interface{})
	for name, service := range sm.services {
		status[name] = gin.H{
			"name":       service.Name,
			"pid":        service.PID,
			"status":     sm.CheckStatus(name),
			"start_time": service.StartTime.Format(time.RFC3339),
			"port":       service.Port,
			"url":        service.URL,
		}
	}
	c.JSON(http.StatusOK, status)
}

// Start individual service
func (sm *SystemManager) startServiceHandler(c *gin.Context) {
	name := c.Param("service")
	var result error
	
	if name == "all" {
		result = sm.startAllServices()
	} else {
		switch name {
		case "api":
			result = sm.StartService("api", "python", "-u", "backend_api.py")
		case "bot":
			result = sm.StartService("bot", "python", "-u", "complete_telegram_bot.py")
		case "dashboard":
			result = sm.StartService("dashboard", "uvicorn", "web_dashboard:app", "--host", "0.0.0.0", "--port", "8000")
		default:
			c.JSON(http.StatusBadRequest, gin.H{"error": "Unknown service"})
			return
		}
	}
	
	if result == nil {
		c.JSON(http.StatusOK, gin.H{"message": fmt.Sprintf("%s service started successfully", name)})
	} else {
		c.JSON(http.StatusInternalServerError, gin.H{"error": result.Error()})
	}
}

// Stop individual service
func (sm *SystemManager) stopServiceHandler(c *gin.Context) {
	name := c.Param("service")
	var result error
	
	if name == "all" {
		result = sm.stopAllServices()
	} else {
		result = sm.StopService(name)
	}
	
	if result == nil {
		c.JSON(http.StatusOK, gin.H{"message": fmt.Sprintf("%s service stopped", name)})
	} else {
		c.JSON(http.StatusInternalServerError, gin.H{"error": result.Error()})
	}
}

func (sm *SystemManager) startAllServices() error {
	fmt.Println("🚀 Starting ALL services...")
	
	// Start services in sequence with small delays
	err := sm.StartService("api", "python", "-u", "backend_api.py")
	if err != nil {
		fmt.Printf("⚠️ API service failed to start: %v\n", err)
		// Continue anyway
	}
	time.Sleep(2 * time.Second)
	
	err = sm.StartService("dashboard", "uvicorn", "web_dashboard:app", "--host", "0.0.0.0", "--port", "8000")
	if err != nil {
		fmt.Printf("⚠️ Dashboard service failed to start: %v\n", err)
		// Continue anyway
	}
	time.Sleep(2 * time.Second)
	
	err = sm.StartService("bot", "python", "-u", "complete_telegram_bot.py")
	if err != nil {
		fmt.Printf("⚠️ Bot service failed to start: %v\n", err)
		// Continue anyway
	}
	
	fmt.Println("✅ All services started (check individual status for confirmation)")
	return nil
}

func (sm *SystemManager) stopAllServices() error {
	fmt.Println("🛑 Stopping ALL services...")
	
	for name := range sm.services {
		err := sm.StopService(name)
		if err != nil {
			fmt.Printf("⚠️ Error stopping %s: %v\n", name, err)
		}
		time.Sleep(1 * time.Second)
	}
	
	fmt.Println("✅ All services stopped")
	return nil
}

func main() {
	sm := NewSystemManager()
	
	r := gin.Default()
	
	// Web dashboard untuk sistem manajemen
	r.LoadHTMLGlob("templates/*")
	r.Static("/static", "./static")
	
	// Routes
	r.GET("/", func(c *gin.Context) {
		c.HTML(http.StatusOK, "index.html", gin.H{
			"title": "Cyber Crack Pro v3.0 - System Manager",
			"services": sm.services,
		})
	})
	
	r.GET("/status", sm.getAllStatus)
	r.POST("/start/:service", sm.startServiceHandler)
	r.POST("/stop/:service", sm.stopServiceHandler)
	r.POST("/restart/:service", func(c *gin.Context) {
		name := c.Param("service")
		
		if name == "all" {
			sm.stopAllServices()
			time.Sleep(3 * time.Second)
			sm.startAllServices()
			c.JSON(http.StatusOK, gin.H{"message": "All services restarted"})
			return
		}
		
		err := sm.StopService(name)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		
		time.Sleep(2 * time.Second)
		
		var startErr error
		switch name {
		case "api":
			startErr = sm.StartService("api", "python", "-u", "backend_api.py")
		case "bot":
			startErr = sm.StartService("bot", "python", "-u", "complete_telegram_bot.py")
		case "dashboard":
			startErr = sm.StartService("dashboard", "uvicorn", "web_dashboard:app", "--host", "0.0.0.0", "--port", "8000")
		default:
			c.JSON(http.StatusBadRequest, gin.H{"error": "Unknown service"})
			return
		}
		
		if startErr == nil {
			c.JSON(http.StatusOK, gin.H{"message": fmt.Sprintf("%s service restarted", name)})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": startErr.Error()})
		}
	})
	
	// Jalankan service-manager di startup
	go func() {
		time.Sleep(1 * time.Second)  // Tunggu web server start
		sm.startAllServices()
	}()
	
	fmt.Println("🚀 Cyber Crack Pro v3.0 - System Manager (Go Version)")
	fmt.Println("🔗 Management Dashboard: http://localhost:8080")
	fmt.Println("📊 API Status: http://localhost:8080/status")
	fmt.Println("🔧 Management Endpoints:")
	fmt.Println("   POST /start/:service - Start a service (api, bot, dashboard, all)")
	fmt.Println("   POST /stop/:service  - Stop a service (api, bot, dashboard, all)")
	fmt.Println("   POST /restart/:service - Restart a service (api, bot, dashboard, all)")
	fmt.Println()
	fmt.Println("⚡ All services will be managed automatically!")
	
	log.Fatal(r.Run(":8080"))
}