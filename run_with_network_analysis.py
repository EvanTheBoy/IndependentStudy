"""
Run Instagram automation with automatic network traffic capture and analysis
"""
import subprocess
import time
import sys
from pathlib import Path
from datetime import datetime

CAPTURE_DIR = Path("network_captures")
CAPTURE_DIR.mkdir(exist_ok=True)

def main():
    print("\n" + "="*60)
    print("INSTAGRAM AUTOMATION WITH NETWORK ANALYSIS")
    print("="*60)
    print("\nThis script will:")
    print("1. Start network traffic capture (requires sudo)")
    print("2. Run Instagram automation")
    print("3. Stop capture and analyze results")
    print("="*60 + "\n")
    
    # Prepare filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pcap_file = CAPTURE_DIR / f"instagram_{timestamp}.pcap"
    
    print(f"Capture file: {pcap_file}\n")
    print("Starting network capture (you'll need to enter sudo password)...")
    
    # Start tcpdump
    tcpdump_cmd = [
        "sudo", "tcpdump",
        "-i", "en0",
        "-w", str(pcap_file),
        "-U"
    ]
    
    tcpdump_process = subprocess.Popen(
        tcpdump_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print("✓ Network capture started")
    time.sleep(2)
    
    # Run automation
    print("\n" + "="*60)
    print("RUNNING INSTAGRAM AUTOMATION")
    print("="*60 + "\n")
    
    try:
        automation_result = subprocess.run(
            ["python", "instagram_automation.py"],
            check=True
        )
        
        print("\n✓ Automation completed successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Automation failed with error code {e.returncode}")
    except KeyboardInterrupt:
        print("\n\n⚠ Automation interrupted by user")
    
    # Stop tcpdump
    print("\n" + "="*60)
    print("STOPPING NETWORK CAPTURE")
    print("="*60 + "\n")
    
    tcpdump_process.terminate()
    tcpdump_process.wait(timeout=5)
    
    print("✓ Capture stopped")
    
    # Analyze capture
    print("\n" + "="*60)
    print("ANALYZING NETWORK TRAFFIC")
    print("="*60 + "\n")
    
    # Basic analysis
    print("Running analysis...")
    
    # Count packets
    result = subprocess.run(
        ["tcpdump", "-r", str(pcap_file), "-n"],
        capture_output=True,
        text=True
    )
    
    lines = result.stdout.strip().split('\n')
    total_packets = len([l for l in lines if l])
    
    print(f"\n📊 RESULTS:")
    print(f"  Total packets: {total_packets}")
    print(f"  Capture file: {pcap_file}")
    print(f"  File size: {pcap_file.stat().st_size / 1024:.2f} KB")
    
    # Protocol breakdown
    tcp_count = len([l for l in lines if 'tcp' in l.lower()])
    udp_count = len([l for l in lines if 'udp' in l.lower()])
    
    print(f"\n  Protocol breakdown:")
    print(f"    TCP: {tcp_count} ({tcp_count/total_packets*100:.1f}%)")
    print(f"    UDP: {udp_count} ({udp_count/total_packets*100:.1f}%)")
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    
    print(f"\nNext steps:")
    print(f"1. View in Wireshark: open {pcap_file}")
    print(f"2. View packets: tcpdump -r {pcap_file} -n | less")
    print(f"3. Filter HTTPS: tcpdump -r {pcap_file} -n 'port 443' | less")
    print(f"4. See hosts: tcpdump -r {pcap_file} -n | awk '{{print $3}}' | sort | uniq")
    print()


if __name__ == "__main__":
    main()
