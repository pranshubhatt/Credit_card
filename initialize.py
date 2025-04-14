import os
import subprocess
import sys
from dotenv import load_dotenv

def check_prerequisites():
    """Check if all prerequisites are installed"""
    print("Checking prerequisites...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        raise RuntimeError("Python 3.8 or higher is required")
    print("✓ Python version OK")
    
    # Check if Docker is installed
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        print("✓ Docker is installed")
    except:
        raise RuntimeError("Docker is not installed")
    
    # Check if Docker Compose is installed
    try:
        subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
        print("✓ Docker Compose is installed")
    except:
        raise RuntimeError("Docker Compose is not installed")

def create_directories():
    """Create necessary directories"""
    print("\nCreating directories...")
    directories = ['logs', 'models', 'api/migrations']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created {directory} directory")

def setup_environment():
    """Set up environment variables"""
    print("\nChecking environment variables...")
    load_dotenv()
    required_vars = [
        "MODEL_PATH",
        "SCALER_PATH",
        "DATABASE_URL",
        "API_KEY",
        "ENVIRONMENT",
        "LOG_LEVEL"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise RuntimeError(f"Missing environment variables: {', '.join(missing_vars)}")
    print("✓ Environment variables OK")

def install_dependencies():
    """Install Python dependencies"""
    print("\nInstalling dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        raise RuntimeError("Failed to install dependencies")

def initialize_database():
    """Initialize the database"""
    print("\nInitializing database...")
    try:
        # Create migration directory if it doesn't exist
        os.makedirs("api/migrations", exist_ok=True)
        
        # Initialize alembic
        subprocess.run(["alembic", "init", "api/migrations"], check=True)
        
        # Create initial migration
        subprocess.run(["alembic", "revision", "--autogenerate", "-m", "Initial migration"], check=True)
        
        # Apply migration
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("✓ Database initialized successfully")
    except subprocess.CalledProcessError:
        raise RuntimeError("Failed to initialize database")

def main():
    """Main initialization function"""
    print("Starting project initialization...\n")
    try:
        check_prerequisites()
        create_directories()
        setup_environment()
        install_dependencies()
        initialize_database()
        
        print("\n✓ Project initialized successfully!")
        print("\nNext steps:")
        print("1. Start the application: docker-compose up --build")
        print("2. Access the API documentation: http://localhost:8000/docs")
        print("3. Run tests: pytest tests/")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 