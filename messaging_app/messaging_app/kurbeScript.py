#!/usr/bin/env python3
"""
kurbeScript.py - Simple Kubernetes Setup Script
This script helps you start a local Kubernetes cluster and check if it's working
"""

import subprocess
import time
import shutil


def print_info(message):
    """Print green info message"""
    print(f"✅ {message}")


def print_error(message):
    """Print red error message"""
    print(f"❌ {message}")


def print_warning(message):
    """Print yellow warning message"""
    print(f"⚠️ {message}")


def print_header(message):
    """Print blue header message"""
    print(f"\n🔷 {message}")
    print("=" * 50)


def check_if_installed(program_name):
    """Check if a program is installed on the computer"""
    return shutil.which(program_name) is not None


def run_command(command_list, show_output=True):
    """
    Run a command and return if it worked
    command_list: list of command parts like ['kubectl', 'get', 'pods']
    show_output: True to show command output, False to hide it
    """
    try:
        if show_output:
            # Show the command output to the user
            result = subprocess.run(command_list, timeout=300)
            return result.returncode == 0
        else:
            # Hide the command output
            result = subprocess.run(command_list, capture_output=True, timeout=300)
            return result.returncode == 0
    except Exception:
        return False


def check_prerequisites():
    """Check if minikube and kubectl are installed"""
    print_info("Checking if required programs are installed...")
    
    # Check if minikube is installed
    if not check_if_installed("minikube"):
        print_error("minikube is not installed!")
        return False
    else:
        print_info("minikube is installed!")
    
    # Check if kubectl is installed
    if not check_if_installed("kubectl"):
        print_error("kubectl is not installed!")
        return False
    else:
        print_info("kubectl is installed!")
    
    return True


def check_minikube_status():
    """Check if minikube is already running"""
    print_info("Checking if minikube is already running...")
    
    # Try to get minikube status
    result = run_command(["minikube", "status"], show_output=False)
    
    if result:
        print_warning("minikube is already running!")
        return True
    else:
        print_info("minikube is not running, we'll start it")
        return False


def start_minikube():
    """Start minikube cluster"""
    print_info("Starting minikube cluster (this might take a few minutes)...")
    
    # Start minikube with basic settings
    success = run_command([
        "minikube", "start",
        "--driver=docker",
        "--cpus=2",
        "--memory=2048"
    ])
    
    if success:
        print_info("minikube started successfully! 🎉")
        return True
    else:
        print_error("Failed to start minikube")
        return False


def verify_cluster():
    """Check if the cluster is working with kubectl cluster-info"""
    print_info("Waiting for cluster to be ready...")
    time.sleep(5)  # Wait 5 seconds
    
    print_info("Checking cluster info...")
    print_header("Cluster Information")
    
    success = run_command(["kubectl", "cluster-info"])
    
    if success:
        print_info("Cluster is working! ✨")
        return True
    else:
        print_error("Cluster is not responding")
        return False


def get_cluster_nodes():
    """Show the cluster nodes"""
    print_header("Cluster Nodes")
    run_command(["kubectl", "get", "nodes"])


def get_all_pods():
    """Show all pods in the cluster"""
    print_header("All Pods in the Cluster")
    run_command(["kubectl", "get", "pods", "--all-namespaces"])


def get_default_pods():
    """Show pods in the default namespace"""
    print_header("Pods in Default Namespace")
    run_command(["kubectl", "get", "pods"])


def show_additional_info():
    """Show extra information about the cluster"""
    print_header("Namespaces")
    run_command(["kubectl", "get", "namespaces"])
    
    print_header("Services")
    run_command(["kubectl", "get", "services", "--all-namespaces"])


def show_helpful_commands():
    """Show useful commands for the user"""
    print_header("Useful Commands")
    print("Here are some commands you can try:")
    print("  📊 kubectl cluster-info          # Show cluster info")
    print("  📦 kubectl get pods              # List pods")
    print("  🌐 kubectl get services          # List services")
    print("  🖥️  minikube dashboard           # Open web dashboard")
    print("  ⏹️  minikube stop               # Stop the cluster")
    print("  🗑️  minikube delete             # Delete the cluster")


def main():
    """Main function that runs everything"""
    print_header("Kubernetes Local Cluster Setup")
    print("Welcome! This script will help you set up Kubernetes locally")
    
    try:
        # Step 1: Check if required programs are installed
        if not check_prerequisites():
            print_error("Please install the missing programs and try again")
            return
        
        # Step 2: Check if minikube is already running
        is_running = check_minikube_status()
        
        # Step 3: Start minikube if it's not running
        if not is_running:
            if not start_minikube():
                print_error("Could not start minikube")
                return
        
        # Step 4: Verify the cluster is working
        if not verify_cluster():
            print_error("Cluster is not working properly")
            return
        
        # Step 5: Show cluster information
        get_cluster_nodes()
        get_all_pods()
        get_default_pods()
        show_additional_info()
        
        # Step 6: Show helpful commands
        show_helpful_commands()
        
        print_info("Setup complete! Your Kubernetes cluster is ready! 🚀")
        
    except KeyboardInterrupt:
        print_warning("Setup was cancelled by user")
    except Exception as error:
        print_error(f"Something went wrong: {error}")


# This runs the main function when the script is executed
if __name__ == "__main__":
    main()