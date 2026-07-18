package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
)

// Stores our 8-bit signal state (0-255) in server RAM
var signalByte byte = 0

// Route 1: Handles raw 8-bit binary GET/POST requests from Roblox & Arduino
func handleSignal(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodPost {
		body, err := io.ReadAll(r.Body)
		// FIXED: Extract the first index body[0] from the byte slice
		if err == nil && len(body) > 0 {
			signalByte = body[0]
			fmt.Printf("📡 Received Bits: %08b (Decimal: %d)\n", signalByte, signalByte)
		}
	}
	w.Header().Set("Content-Type", "application/octet-stream")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte{signalByte})
}

// Route 2: Renders a plain web view that displays the bits directly on screen
func handleWebView(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	
	html := fmt.Sprintf(`
	<!DOCTYPE html>
	<html>
	<head>
		<title>8-Bit Signal Monitor</title>
		<meta http-equiv="refresh" content="1">
		<style>
			body { font-family: monospace; background: #121212; color: #00ff00; padding: 40px; font-size: 24px; line-height: 1.6; }
			.container { max-width: 500px; margin: 0 auto; border: 1px solid #00ff00; padding: 20px; border-radius: 5px; background: #1a1a1a; }
			h2 { color: #ffffff; margin-top: 0; border-bottom: 1px solid #00ff00; padding-bottom: 10px; }
			span { color: #ffff00; font-weight: bold; }
		</style>
	</head>
	<body>
		<div class="container">
			<h2>🕹️ 8-Bit Logic Status</h2>
			<div>Binary Bits : <span>%%08b</span></div>
			<div>Decimal Value: <span>%%d</span></div>
		</div>
	</body>
	</html>`, signalByte, signalByte)

	w.Write([]byte(html))
}

func main() {
	http.HandleFunc("/signal", handleSignal) // For Roblox/Arduino
	http.HandleFunc("/", handleWebView)      // Displays data right on screen
	
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	http.ListenAndServe(":"+port, nil)
}
