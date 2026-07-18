package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
)

// Stores our 8-bit signal state (0-255) in server RAM
var signalByte byte = 0

func handleSignal(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodPost {
		// Read the raw 1-byte payload coming from Roblox Build Logic
		body, err := io.ReadAll(r.Body)
		if err == nil && len(body) > 0 {
			signalByte = body[0]
			// Prints the bits inside the server logs (e.g., 00001111)
			fmt.Printf("📡 Received Bits: %08b (Decimal: %d)\n", signalByte, signalByte)
		}
	}

	// Respond back with the raw 1-byte stream data
	w.Header().Set("Content-Type", "application/octet-stream")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte{signalByte})
}

func main() {
	// A single clean endpoint handling both GET and POST requests
	http.HandleFunc("/signal", handleSignal)

	// Fetch port assigned by cloud host (Render defaults to 8080)
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	fmt.Printf("🏎️ High-Speed Go API listening on port %s...\n", port)
	http.ListenAndServe(":"+port, nil)
}
