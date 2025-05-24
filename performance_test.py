#!/usr/bin/env python3
"""
Performance test script to measure application startup time
"""
import time
import subprocess
import statistics
import sys

def run_test(command, iterations=5):
    """Run the specified command multiple times and measure execution time"""
    times = []
    
    print(f"Running performance test for: {command}")
    print(f"Performing {iterations} iterations...")
    
    for i in range(iterations):
        start_time = time.time()
        process = subprocess.run(command, shell=True, capture_output=True)
        end_time = time.time()
        
        if process.returncode != 0:
            print(f"Error running command: {process.stderr.decode('utf-8')}")
            continue
            
        execution_time = end_time - start_time
        times.append(execution_time)
        print(f"  Iteration {i+1}: {execution_time:.4f} seconds")
    
    if not times:
        print("All iterations failed!")
        return None
    
    avg_time = statistics.mean(times)
    median_time = statistics.median(times)
    min_time = min(times)
    max_time = max(times)
    
    print("\nResults:")
    print(f"  Average time: {avg_time:.4f} seconds")
    print(f"  Median time: {median_time:.4f} seconds")
    print(f"  Min time: {min_time:.4f} seconds")
    print(f"  Max time: {max_time:.4f} seconds")
    
    return {
        "avg": avg_time,
        "median": median_time,
        "min": min_time,
        "max": max_time,
        "all_times": times
    }

def check_command_exists(command):
    """Check if a command exists in the system"""
    try:
        subprocess.run(command.split()[0], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

def main():
    """Main function to run performance tests"""
    # Default to 3 iterations if not specified
    iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    
    print("=" * 50)
    print("PERFORMANCE TEST - STARTUP TIME")
    print("=" * 50)
    
    # Test python3 main.py
    python_results = run_test("python3 main.py --check-startup-only", iterations)
    
    print("\n" + "=" * 50)
    
    # Test uv run if uv is available
    if check_command_exists("uv --version"):
        print("Found uv package manager, testing with 'uv run'")
        try:
            uv_results = run_test("uv run python main.py --check-startup-only", iterations)
            
            if python_results and uv_results:
                print("\nComparison:")
                if uv_results['avg'] > python_results['avg']:
                    print(f"  uv run is {uv_results['avg'] / python_results['avg']:.2f}x slower than standard Python")
                else:
                    print(f"  uv run is {python_results['avg'] / uv_results['avg']:.2f}x faster than standard Python")
        except Exception as e:
            print(f"Error running uv test: {e}")
    else:
        print("uv package manager not found, skipping uv test")
    
    print("=" * 50)

if __name__ == "__main__":
    main()