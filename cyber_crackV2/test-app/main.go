package main

import (
	"log"
	"os"
	"path/filepath"

	"github.com/gin-gonic/gin"
)

func main() {
	// Set release mode if not in debug mode
	if os.Getenv("DEBUG") != "true" {
		gin.SetMode(gin.ReleaseMode)
	}

	router := gin.Default()

	// Define upload path from environment variable or use default
	uploadPath := os.Getenv("UPLOAD_PATH")
	if uploadPath == "" {
		uploadPath = "./uploads"
	}

	// Create uploads directory if it doesn't exist
	if err := os.MkdirAll(uploadPath, os.ModePerm); err != nil {
		log.Fatal("Failed to create upload directory:", err)
	}

	// Serve static files
	router.Static("/static", "./static")
	
	// Set up template directory
	router.LoadHTMLGlob("templates/*")

	// Import routes
	setupRoutes(router, uploadPath)

	// Determine port from environment variable or use default
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("Server starting on port %s\n", port)
	log.Printf("Upload path: %s\n", uploadPath)
	
	if err := router.Run(":" + port); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}