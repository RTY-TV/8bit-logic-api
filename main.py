from flask import Flask, request, render_template_string

app = Flask(__name__)

# Global storage for our 8-bit signal (0 to 255)
signal_byte = 0

@app.route('/signal', methods=['GET', 'POST'])
def handle_signal():
    global signal_byte
    
    if request.method == 'POST':
        # Safely extracts the data from the 'value' input box inside your green block
        val_str = request.form.get('value', '')
        
        if val_str:
            try:
                # Case A: If Build Logic sends a decimal integer (e.g., "15")
                signal_byte = int(val_str)
            except ValueError:
                try:
                    # Case B: If Build Logic sends a raw binary string (e.g., "00001111")
                    signal_byte = int(val_str, 2)
                except ValueError:
                    pass
            print(f"📡 Signal Updated: {bin(signal_byte)[2:].zfill(8)} (Decimal: {signal_byte})")

    # Return the clean current state back to the game as a fast plain-text string
    return str(signal_byte), 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/')
def handle_web_view():
    global signal_byte
    
    # Generate human-readable string formats for our auto-refreshing interface
    binary_text = bin(signal_byte)[2:].zfill(8)
    decimal_text = str(signal_byte)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>8-Bit Signal Monitor</title>
        <style>
            body {{ font-family: monospace; background: #121212; color: #00ff00; padding: 40px; font-size: 24px; line-height: 1.6; }}
            .container {{ max-width: 500px; margin: 0 auto; border: 1px solid #00ff00; padding: 20px; border-radius: 5px; background: #1a1a1a; }}
            h2 {{ color: #ffffff; margin-top: 0; border-bottom: 1px solid #00ff00; padding-bottom: 10px; }}
            span {{ color: #ffff00; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🕹️ 8-Bit Logic Status</h2>
            <div>Binary Bits : <span id="bits">{binary_text}</span></div>
            <div>Decimal Value: <span id="dec">{decimal_text}</span></div>
        </div>

        <script>
            // Background interval that forces sync and feeds UptimeRobot every 1s
            setInterval(() => {{
                fetch('/signal')
                    .then(res => res.text())
                    .then(text => {{
                        let num = parseInt(text) || 0;
                        document.getElementById('bits').innerText = num.toString(2).padStart(8, '0');
                        document.getElementById('dec').innerText = num.toString(10);
                    }}).catch(err => console.log("Ping failed..."));
            }}, 1000);
        </script>
    </body>
    </html>"""
    return render_template_string(html)

if __name__ == '__main__':
    app.run()
