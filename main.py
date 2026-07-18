from flask import Flask, request, render_template_string

app = Flask(__name__)

# Global storage for our 8-bit signal (0 to 255)
signal_byte = 0

@app.route('/signal', methods=['GET', 'POST'])
def handle_signal():
    global signal_byte
    if request.method == 'POST':
        val_str = request.form.get('value', '')
        if val_str:
            try:
                signal_byte = int(val_str)
            except ValueError:
                try:
                    signal_byte = int(val_str, 2)
                except ValueError:
                    pass
            print(f"📡 Signal via Roblox: {signal_byte}")

    return str(signal_byte), 200, {'Content-Type': 'text/plain; charset=utf-8'}

# New route that lets your browser buttons change the cloud data
@app.route('/set_value', methods=['POST'])
def set_value():
    global signal_byte
    val = request.data.decode('utf-8')
    if val.isdigit():
        signal_byte = int(val) & 0xFF  # Bound to 8-bit max (255)
        return "OK", 200
    return "Error", 400

@app.route('/')
def handle_web_view():
    global signal_byte
    binary_text = bin(signal_byte)[2:].zfill(8)
    decimal_text = str(signal_byte)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>8-Bit Signal Monitor</title>
        <style>
            body {{ font-family: monospace; background: #121212; color: #00ff00; padding: 40px; font-size: 24px; text-align: center; }}
            .container {{ max-width: 600px; margin: 0 auto; border: 1px solid #00ff00; padding: 20px; border-radius: 5px; background: #1a1a1a; }}
            h2 {{ color: #ffffff; margin-top: 0; border-bottom: 1px solid #00ff00; padding-bottom: 10px; }}
            span {{ color: #ffff00; font-weight: bold; }}
            .bit-row {{ display: flex; justify-content: center; gap: 10px; margin: 25px 0; }}
            .bit-btn {{ background: #333; color: #888; border: 2px solid #555; padding: 10px 15px; border-radius: 4px; font-weight: bold; cursor: pointer; font-family: monospace; font-size: 18px; }}
            .bit-btn.active {{ background: #00ff00; color: #000; border-color: #00ff00; box-shadow: 0 0 10px #00ff00; }}
            .input-box {{ background: #000; border: 1px solid #00ff00; color: #ffff00; padding: 8px; font-size: 18px; font-family: monospace; width: 100px; text-align: center; border-radius: 4px; }}
            .submit-btn {{ background: #00ff00; color: #000; font-weight: bold; padding: 8px 15px; font-size: 18px; border: none; cursor: pointer; border-radius: 4px; margin-left: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🕹️ Interactive 8-Bit Controller</h2>
            <div>Binary Bits : <span id="bits">{binary_text}</span></div>
            <div>Decimal Value: <span id="dec">{decimal_text}</span></div>

            <!-- Clickable Interactive Bits Row -->
            <div class="bit-row">
                <button class="bit-btn" onclick="toggleBit(7)">B7</button>
                <button class="bit-btn" onclick="toggleBit(6)">B6</button>
                <button class="bit-btn" onclick="toggleBit(5)">B5</button>
                <button class="bit-btn" onclick="toggleBit(4)">B4</button>
                <button class="bit-btn" onclick="toggleBit(3)">B3</button>
                <button class="bit-btn" onclick="toggleBit(2)">B2</button>
                <button class="bit-btn" onclick="toggleBit(1)">B1</button>
                <button class="bit-btn" onclick="toggleBit(0)">B0</button>
            </div>

            <!-- Custom Number Entry Field -->
            <div>
                <input type="number" id="numInput" class="input-box" min="0" max="255" placeholder="0-255">
                <button class="submit-btn" onclick="sendInputVal()">Set</button>
            </div>
        </div>

        <script>
            let currentVal = {signal_byte};

            // Updates active/inactive styles on buttons based on bits
            function updateButtonUI(val) {{
                for(let i=0; i<8; i++) {{
                    let btn = document.querySelectorAll('.bit-btn')[7-i];
                    if(((val >> i) & 1) === 1) {{
                        btn.classList.add('active');
                        btn.innerText = "1";
                    }} else {{
                        btn.classList.remove('active');
                        btn.innerText = "0";
                    }}
                }}
            }}

            // Handles clicking a bit button
            function toggleBit(bitIndex) {{
                currentVal ^= (1 << bitIndex); // XOR bitflip
                sendValueToServer(currentVal);
            }}

            // Handles typing a custom number
            function sendInputVal() {{
                let val = parseInt(document.getElementById('numInput').value);
                if(!isNaN(val) && val >= 0 && val <= 255) {{
                    currentVal = val;
                    sendValueToServer(currentVal);
                }}
            }}

            function sendValueToServer(val) {{
                fetch('/set_value', {{ method: 'POST', body: val.toString() }});
            }}

            // Keep UI refreshing smoothly every 1 second
            setInterval(() => {{
                fetch('/signal')
                    .then(res => res.text())
                    .then(text => {{
                        let num = parseInt(text) || 0;
                        currentVal = num;
                        document.getElementById('bits').innerText = num.toString(2).padStart(8, '0');
                        document.getElementById('dec').innerText = num.toString(10);
                        updateButtonUI(num);
                    }});
            }}, 1000);

            updateButtonUI(currentVal);
        </script>
    </body>
    </html>"""
    return render_template_string(html)

if __name__ == '__main__':
    app.run()
