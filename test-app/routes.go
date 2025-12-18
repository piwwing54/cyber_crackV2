package main

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func setupRoutes(router *gin.Engine, uploadPath string) {
	// Public routes
	router.GET("/", func(c *gin.Context) {
		c.HTML(http.StatusOK, "index.html", gin.H{
			"title": "APK Security Test Manager",
		})
	})

	// File upload route
	router.POST("/upload", func(c *gin.Context) {
		handleFileUpload(c, uploadPath)
	})

	// File management routes
	router.GET("/files", func(c *gin.Context) {
		listFiles(c, uploadPath)
	})
	
	router.DELETE("/files/:filename", func(c *gin.Context) {
		deleteFile(c, uploadPath)
	})

	// Security testing routes
	router.GET("/test/:filename", func(c *gin.Context) {
		testFile(c, uploadPath)
	})

	// Serve API documentation
	router.GET("/docs", func(c *gin.Context) {
		c.HTML(http.StatusOK, "docs.html", gin.H{
			"title": "API Documentation",
		})
	})
}