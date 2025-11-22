"""
Network Traffic Analyzer for Instagram Automation
Captures and analyzes network traffic patterns during automation
"""
import subprocess
import time
import json
import signal
import sys
from datetime import datetime
from pathlib import Path

# Configuration
CAPTURE_DIR = Path("network_captures")
CAPTURE_DIR.mkdir(exist_ok=True)

class NetworkAnalyzer:
    def __init__(self, interface="en0"):
        self.interface = interface
        self.capture_file = None
        self.tcpdump_process = None
        self.start_time = None
        
    def start_capture(self, name="instagram_traffic"):
        """Start capturing network traffic"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.capture_file = CAPTURE_DIR / f"{name}_{timestamp}.pcap"
        
        print(f"\n{'='*60}")
        print("NETWORK TRAFFIC CAPTURE STARTED")
        print(f"{'='*60}")
        print(f"Interface: {self.interface}")
        print(f"Capture file: {self.capture_file}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        # Start tcpdump in background
        cmd = [
            "sudo", "tcpdump",
            "-i", self.interface,
            "-w", str(self.capture_file),
            "-U"  # Unbuffered output
        ]
        
        self.tcpdump_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        self.start_time = time.time()
        time.sleep(2)  # Give tcpdump time to start
        
        return self.capture_file
    
    def stop_capture(self):
        """Stop capturing network traffic"""
        if self.tcpdump_process:
            print(f"\n{'='*60}")
            print("STOPPING NETWORK CAPTURE...")
            print(f"{'='*60}\n")
            
            # Send SIGINT to tcpdump
            self.tcpdump_process.send_signal(signal.SIGINT)
            self.tcpdump_process.wait(timeout=5)
            
            duration = time.time() - self.start_time
            
            print(f"Capture stopped")
            print(f"Duration: {duration:.2f} seconds")
            print(f"Saved to: {self.capture_file}\n")
            
            return self.capture_file
        
        return None
    
    def analyze_capture(self, pcap_file=None):
        """Analyze the captured traffic"""
        if pcap_file is None:
            pcap_file = self.capture_file
        
        if not pcap_file or not Path(pcap_file).exists():
            print("No capture file to analyze")
            return None
        
        print(f"\n{'='*60}")
        print("NETWORK TRAFFIC ANALYSIS")
        print(f"{'='*60}\n")
        
        analysis = {}
        
        # Total packet count
        result = subprocess.run(
            ["tcpdump", "-r", str(pcap_file), "-n"],
            capture_output=True,
            text=True
        )
        total_packets = len(result.stdout.strip().split('\n'))
        analysis['total_packets'] = total_packets
        
        print(f"Total packets captured: {total_packets}")
        
        # Protocol distribution
        print("\nProtocol Distribution:")
        protocols = {}
        for line in result.stdout.split('\n'):
            if 'IP' in line:
                if 'tcp' in line.lower():
                    protocols['TCP'] = protocols.get('TCP', 0) + 1
                elif 'udp' in line.lower():
                    protocols['UDP'] = protocols.get('UDP', 0) + 1
                elif 'icmp' in line.lower():
                    protocols['ICMP'] = protocols.get('ICMP', 0) + 1
        
        for proto, count in protocols.items():
            percentage = (count / total_packets * 100) if total_packets > 0 else 0
            print(f"  {proto}: {count} ({percentage:.1f}%)")
        
        analysis['protocols'] = protocols
        
        # Unique hosts
        hosts = set()
        for line in result.stdout.split('\n'):
            parts = line.split()
            for i, part in enumerate(parts):
                if '>' in part and i > 0:
                    src = parts[i-1].split('.')[0] if '.' in parts[i-1] else parts[i-1]
                    dst = parts[i+1].split('.')[0] if '.' in parts[i+1] else parts[i+1]
                    if src: hosts.add(src)
                    if dst: hosts.add(dst)
        
        print(f"\nUnique hosts: {len(hosts)}")
        analysis['unique_hosts'] = len(hosts)
        
        # Traffic over time (packets per second)
        if self.start_time:
            duration = time.time() - self.start_time
            pps = total_packets / duration if duration > 0 else 0
            print(f"Average packets per second: {pps:.2f}")
            analysis['packets_per_second'] = pps
            analysis['duration_seconds'] = duration
        
        # Save analysis to JSON
        analysis_file = Path(str(pcap_file).replace('.pcap', '_analysis.json'))
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"\nAnalysis saved to: {analysis_file}")
        print(f"{'='*60}\n")
        
        return analysis


def main():
    """Run network capture with automation"""
    print("\n" + "="*60)
    print("INSTAGRAM AUTOMATION WITH NETWORK ANALYSIS")
    print("="*60)
    print("\nThis will:")
    print("1. Start capturing network traffic")
    print("2. Run the Instagram automation")
    print("3. Stop capture and analyze traffic")
    print("\nYou'll need to enter your sudo password for tcpdump.")
    print("="*60 + "\n")
    
    input("Press Enter to start...")
    
    # Initialize analyzer
    analyzer = NetworkAnalyzer(interface="en0")
    
    try:
        # Start capture
        capture_file = analyzer.start_capture("instagram_automation")
        
        print("Network capture is running...")
        print("Now run your automation in another terminal:")
        print("  python instagram_automation.py")
        print("\nPress Ctrl+C when automation is complete to stop capture\n")
        
        # Wait for user to stop
        signal.pause()
        
    except KeyboardInterrupt:
        print("\n\nStopping capture...")
        
    finally:
        # Stop capture and analyze
        pcap_file = analyzer.stop_capture()
        
        if pcap_file:
            analyzer.analyze_capture(pcap_file)
            
            print("\nNext steps:")
            print(f"1. View capture in Wireshark: open {pcap_file}")
            print(f"2. Read packets: tcpdump -r {pcap_file} -n | less")
            print(f"3. Filter HTTPS: tcpdump -r {pcap_file} -n 'port 443'")


if __name__ == "__main__":
    main()
