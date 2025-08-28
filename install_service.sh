#!/bin/bash

# mcp-mem0 Systemd Service Installer
# This script will create and configure the systemd service for mcp-mem0

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVICE_NAME="mcp-mem0"
SERVICE_USER="tarina"
PROJECT_DIR="/home/tarina/mcp-mem0"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Function to check if user exists
check_user() {
    if ! id "$SERVICE_USER" &>/dev/null; then
        print_error "User '$SERVICE_USER' does not exist"
        exit 1
    fi
}

# Function to check if project directory exists
check_project_dir() {
    if [[ ! -d "$PROJECT_DIR" ]]; then
        print_error "Project directory '$PROJECT_DIR' does not exist"
        exit 1
    fi
}

# Function to check if .env file exists
check_env_file() {
    if [[ ! -f "$PROJECT_DIR/.env" ]]; then
        print_warning ".env file not found in project directory"
        print_status "You can create one using: python configure_env.py"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Installation cancelled"
            exit 1
        fi
    fi
}

# Function to check if virtual environment exists
check_venv() {
    if [[ ! -d "$PROJECT_DIR/.venv" ]]; then
        print_warning "Virtual environment not found in project directory"
        print_status "You can create one using: python -m venv .venv"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Installation cancelled"
            exit 1
        fi
    fi
}

# Function to create systemd service file
create_service_file() {
    print_status "Creating systemd service file..."
    
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=MCP Mem0 AI Memory Server
After=network.target
Wants=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/.venv/bin/python src/main.py
Restart=always
RestartSec=10
TimeoutStopSec=30
KillMode=mixed
KillSignal=SIGTERM

# Load environment variables from .env file
EnvironmentFile=$PROJECT_DIR/.env

# Set working directory and environment
Environment=PWD=$PROJECT_DIR
Environment=PYTHONPATH=$PROJECT_DIR

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$PROJECT_DIR

[Install]
WantedBy=multi-user.target
EOF

    print_success "Service file created at $SERVICE_FILE"
}

# Function to set proper permissions
set_permissions() {
    print_status "Setting proper permissions..."
    
    # Set ownership of service file
    chown root:root "$SERVICE_FILE"
    chmod 644 "$SERVICE_FILE"
    
    # Set ownership of project directory
    chown -R "$SERVICE_USER:$SERVICE_USER" "$PROJECT_DIR"
    
    print_success "Permissions set correctly"
}

# Function to reload systemd and enable service
enable_service() {
    print_status "Reloading systemd daemon..."
    systemctl daemon-reload
    
    print_status "Enabling $SERVICE_NAME service..."
    systemctl enable "$SERVICE_NAME"
    
    print_success "Service enabled successfully"
}

# Function to start service
start_service() {
    print_status "Starting $SERVICE_NAME service..."
    
    if systemctl start "$SERVICE_NAME"; then
        print_success "Service started successfully"
    else
        print_error "Failed to start service"
        print_status "Check the logs with: journalctl -u $SERVICE_NAME -f"
        exit 1
    fi
}

# Function to check service status
check_service_status() {
    print_status "Checking service status..."
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_success "Service is running"
    else
        print_error "Service is not running"
        print_status "Check the logs with: journalctl -u $SERVICE_NAME -f"
        exit 1
    fi
}

# Function to show service information
show_service_info() {
    print_status "Service Information:"
    echo "Service Name: $SERVICE_NAME"
    echo "Service File: $SERVICE_FILE"
    echo "Project Directory: $PROJECT_DIR"
    echo "Service User: $SERVICE_USER"
    echo ""
    
    print_status "Useful commands:"
    echo "  Check status: sudo systemctl status $SERVICE_NAME"
    echo "  View logs: sudo journalctl -u $SERVICE_NAME -f"
    echo "  Restart: sudo systemctl restart $SERVICE_NAME"
    echo "  Stop: sudo systemctl stop $SERVICE_NAME"
    echo "  Disable: sudo systemctl disable $SERVICE_NAME"
}

# Function to backup existing service file
backup_existing_service() {
    if [[ -f "$SERVICE_FILE" ]]; then
        print_warning "Service file already exists"
        backup_file="${SERVICE_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$SERVICE_FILE" "$backup_file"
        print_status "Existing service file backed up to: $backup_file"
        
        read -p "Replace existing service file? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Installation cancelled"
            exit 1
        fi
    fi
}

# Function to uninstall service
uninstall_service() {
    print_status "Uninstalling $SERVICE_NAME service..."
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_status "Stopping service..."
        systemctl stop "$SERVICE_NAME"
    fi
    
    if systemctl is-enabled --quiet "$SERVICE_NAME"; then
        print_status "Disabling service..."
        systemctl disable "$SERVICE_NAME"
    fi
    
    if [[ -f "$SERVICE_FILE" ]]; then
        print_status "Removing service file..."
        rm "$SERVICE_FILE"
    fi
    
    print_status "Reloading systemd daemon..."
    systemctl daemon-reload
    
    print_success "Service uninstalled successfully"
}

# Function to show help
show_help() {
    echo "mcp-mem0 Systemd Service Installer"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  install     Install the systemd service (default)"
    echo "  uninstall   Uninstall the systemd service"
    echo "  status      Check service status"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  sudo $0 install      # Install the service"
    echo "  sudo $0 uninstall    # Uninstall the service"
    echo "  sudo $0 status       # Check service status"
}

# Main installation function
install_service() {
    print_status "Starting installation of $SERVICE_NAME systemd service..."
    echo ""
    
    # Run all checks
    check_root
    check_user
    check_project_dir
    check_env_file
    check_venv
    
    echo ""
    
    # Backup existing service if it exists
    backup_existing_service
    
    # Create service file
    create_service_file
    
    # Set permissions
    set_permissions
    
    # Enable and start service
    enable_service
    start_service
    
    # Check final status
    check_service_status
    
    echo ""
    print_success "Installation completed successfully!"
    echo ""
    
    # Show service information
    show_service_info
}

# Main script logic
main() {
    case "${1:-install}" in
        "install")
            install_service
            ;;
        "uninstall")
            check_root
            uninstall_service
            ;;
        "status")
            if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
                print_success "Service is running"
                systemctl status "$SERVICE_NAME"
            else
                print_warning "Service is not running or not installed"
            fi
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
