from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"Krishi AI REST API starting on port {port}...")
    app.run(debug=True, host="0.0.0.0", port=port)
