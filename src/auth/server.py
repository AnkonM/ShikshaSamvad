#!/usr/bin/env python3
"""
Authentication server - standalone Flask app
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.auth.integration import create_authenticated_app

def main():
    """Run authentication server"""
    print("🚀 Starting ShikshaSamvad Authentication Server...")
    
    # Create authenticated app
    app = create_authenticated_app("sqlite:///data/processed/shikshasamvaad.db")
    
    # Run server
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )

if __name__ == "__main__":
    main()
