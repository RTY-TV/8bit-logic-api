package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
)

var signalByte byte = 0

func handleSignal(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodPost {
		body, err := io.ReadAll(r.Body)
		if err == nil && len(body) > 0 {
			signalByte = body[0]
			fmt.Printf("📡 Received Bits: %08b\n", signalByte)
		}
	}
	w.Header().Set("Content-Type", "application/octet-stream")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte{signalByte})
}

func handleWebView(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	
	binaryText := fmt.Sprintf("%08b", signalByte)
	decimalText := fmt.Sprintf("%d", signalByte)

	html := `
	<!DOCTYPE html>
	<html>
	<head>
		<title>8-Bit Signal Monitor</title>
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
			<div>Binary Bits : <span id="bits">` + binaryText + `</span></div>
			<div>Decimal Value: <span id="dec">` + decimalText + `</span></div>
		</div>

		<script>
			// 1. Instantly fetch and update data every 1 second without reloading the whole page
			setInterval(() => {
				fetch('/signal')
					.then(res => res.arrayBuffer())
					.then(buf => {
						let byte = new Uint8Array(buf)[0] || 0;
						document.getElementById('bits').innerText = byte.toString(2).padStart(8, '0');
						document.getElementById('dec').innerText = byte.toString(10);
					}).catch(err => console.log("Wake-up ping failed..."));
			}, 1000);

			// 2. Anti-Sleep Heartbeat: Keeps pushing an extra web ping every 10 minutes 
			setInterval(() => {
				fetch('/signal').then(() => console.log("💖 Anti-Sleep Heartbeat Sent!"));
			}, 600000); 
		</script>
	</body>
	</html>`

	w.Write([]byte(html))
}

func main() {
	http.HandleFunc("/signal", handleSignal)
	http.HandleFunc("/", handleWebView)
	
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	http.ListenAndServe(":"+port, nil)
}
