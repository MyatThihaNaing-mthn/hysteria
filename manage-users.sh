#!/bin/bash
#
# Hysteria 2 VPN - User Management Script
# This script helps manage users in the Hysteria server configuration
#

set -e

# Configuration
CONFIG_FILE="${CONFIG_FILE:-/etc/hysteria/config.yaml}"
BACKUP_DIR="${BACKUP_DIR:-/etc/hysteria/backups}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "$1"
}

# Check if config file exists
check_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        print_error "Configuration file not found: $CONFIG_FILE"
        print_info "Please specify the correct path using CONFIG_FILE environment variable"
        exit 1
    fi
}

# Create backup of config file
backup_config() {
    mkdir -p "$BACKUP_DIR"
    local backup_file="$BACKUP_DIR/config.yaml.$(date +%Y%m%d_%H%M%S)"
    cp "$CONFIG_FILE" "$backup_file"
    print_success "Backup created: $backup_file"
}

# Generate random password
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-24
}

# List all users
list_users() {
    print_info "\n=== Current Users ==="
    
    if grep -q "type: userpass" "$CONFIG_FILE"; then
        # Extract usernames from userpass section
        awk '/userpass:/,/^[^ ]/ {
            if ($1 ~ /^[a-zA-Z0-9_-]+:/ && $1 !~ /^userpass:/) {
                gsub(/:.*/, "", $1)
                print $1
            }
        }' "$CONFIG_FILE" | nl
        
        local count=$(awk '/userpass:/,/^[^ ]/ {
            if ($1 ~ /^[a-zA-Z0-9_-]+:/ && $1 !~ /^userpass:/) {
                count++
            }
        } END {print count}' "$CONFIG_FILE")
        
        print_info "\nTotal users: $count"
    else
        print_warning "No userpass authentication configured"
    fi
}

# Add a new user
add_user() {
    local username="$1"
    local password="$2"
    
    if [ -z "$username" ]; then
        print_error "Username is required"
        print_info "Usage: $0 add <username> [password]"
        exit 1
    fi
    
    # Validate username
    if [[ ! "$username" =~ ^[a-zA-Z0-9_-]+$ ]]; then
        print_error "Invalid username. Use only letters, numbers, underscore and hyphen"
        exit 1
    fi
    
    # Check if user already exists
    if grep -q "^    $username:" "$CONFIG_FILE"; then
        print_error "User '$username' already exists"
        exit 1
    fi
    
    # Generate password if not provided
    if [ -z "$password" ]; then
        password=$(generate_password)
        print_info "Generated password: $password"
    fi
    
    # Backup config
    backup_config
    
    # Add user to config
    # Find the userpass section and add the new user
    awk -v user="$username" -v pass="$password" '
    /^  userpass:/ {
        print
        in_userpass = 1
        next
    }
    in_userpass && /^  [a-zA-Z]/ {
        print "    " user ": \"" pass "\""
        in_userpass = 0
    }
    in_userpass && /^    [a-zA-Z0-9_-]+:/ {
        if (!printed) {
            print "    " user ": \"" pass "\""
            printed = 1
        }
    }
    { print }
    ' "$CONFIG_FILE" > "$CONFIG_FILE.tmp"
    
    mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"
    
    print_success "User '$username' added successfully"
    print_info "\nCredentials:"
    print_info "  Username: $username"
    print_info "  Password: $password"
    print_warning "\nRemember to restart the Hysteria server for changes to take effect!"
}

# Remove a user
remove_user() {
    local username="$1"
    
    if [ -z "$username" ]; then
        print_error "Username is required"
        print_info "Usage: $0 remove <username>"
        exit 1
    fi
    
    # Check if user exists
    if ! grep -q "^    $username:" "$CONFIG_FILE"; then
        print_error "User '$username' not found"
        exit 1
    fi
    
    # Backup config
    backup_config
    
    # Remove user from config
    sed -i "/^    $username:/d" "$CONFIG_FILE"
    
    print_success "User '$username' removed successfully"
    print_warning "Remember to restart the Hysteria server for changes to take effect!"
}

# Change user password
change_password() {
    local username="$1"
    local new_password="$2"
    
    if [ -z "$username" ]; then
        print_error "Username is required"
        print_info "Usage: $0 password <username> [new_password]"
        exit 1
    fi
    
    # Check if user exists
    if ! grep -q "^    $username:" "$CONFIG_FILE"; then
        print_error "User '$username' not found"
        exit 1
    fi
    
    # Generate password if not provided
    if [ -z "$new_password" ]; then
        new_password=$(generate_password)
        print_info "Generated password: $new_password"
    fi
    
    # Backup config
    backup_config
    
    # Update password
    sed -i "s/^    $username:.*$/    $username: \"$new_password\"/" "$CONFIG_FILE"
    
    print_success "Password for '$username' changed successfully"
    print_info "\nNew credentials:"
    print_info "  Username: $username"
    print_info "  Password: $new_password"
    print_warning "\nRemember to restart the Hysteria server for changes to take effect!"
}

# Restart server
restart_server() {
    print_info "\nRestarting Hysteria server..."
    
    if systemctl is-active --quiet hysteria-server; then
        systemctl restart hysteria-server
        print_success "Server restarted successfully"
    elif command -v docker &> /dev/null && docker ps | grep -q hysteria-server; then
        docker restart hysteria-server
        print_success "Docker container restarted successfully"
    else
        print_warning "Could not detect running server. Please restart manually."
        print_info "  Systemd: sudo systemctl restart hysteria-server"
        print_info "  Docker: docker restart hysteria-server"
    fi
}

# Show usage
usage() {
    cat << EOF
Hysteria 2 VPN - User Management Script

Usage: $0 <command> [arguments]

Commands:
    list                    List all users
    add <username> [pass]   Add a new user (generates password if not provided)
    remove <username>       Remove a user
    password <username> [pass]  Change user password (generates if not provided)
    restart                 Restart the Hysteria server
    backup                  Create a backup of the config file
    help                    Show this help message

Examples:
    $0 list
    $0 add alice
    $0 add bob MySecurePassword123!
    $0 password alice
    $0 remove bob
    $0 restart

Environment Variables:
    CONFIG_FILE    Path to Hysteria config file (default: /etc/hysteria/config.yaml)
    BACKUP_DIR     Path to backup directory (default: /etc/hysteria/backups)

EOF
}

# Main script
main() {
    local command="${1:-help}"
    
    case "$command" in
        list)
            check_config
            list_users
            ;;
        add)
            check_config
            add_user "$2" "$3"
            ;;
        remove)
            check_config
            remove_user "$2"
            ;;
        password|passwd)
            check_config
            change_password "$2" "$3"
            ;;
        restart)
            restart_server
            ;;
        backup)
            check_config
            backup_config
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            print_error "Unknown command: $command"
            usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
