from flask import Flask, render_template, jsonify, request, send_file, redirect, url_for
from scapy.all import sniff
from threading import Thread, Lock
from datetime import datetime
import csv

app = Flask(__name__)

packets = []
packet_counts = []
timestamps = []
capture_thread = None
capture_lock = Lock()
capturing = False


def packet_callback(packet):
    global packets, packet_counts, timestamps
    with capture_lock:
        timestamp = datetime.now().strftime("%H:%M:%S")
        packets.append({
            "time": timestamp,
            "source": packet[0].src if hasattr(packet[0], "src") else "N/A",
            "destination": packet[0].dst if hasattr(packet[0], "dst") else "N/A",
            "protocol": packet.name,
            "length": len(packet)
        })

        if timestamps and timestamps[-1] == timestamp:
            packet_counts[-1] += 1
        else:
            timestamps.append(timestamp)
            packet_counts.append(1)


def start_sniffing():
    sniff(prn=packet_callback, store=0)


@app.route('/')
def landing_page():
    return render_template('landing.html')


@app.route('/sniffer')
def sniffer_page():
    return render_template('index.html')


@app.route('/start')
def start_capture():
    global capturing, capture_thread, packets, packet_counts, timestamps
    if not capturing:
        packets.clear()
        packet_counts.clear()
        timestamps.clear()
        capturing = True
        capture_thread = Thread(target=start_sniffing, daemon=True)
        capture_thread.start()
    return "Sniffing started"


@app.route('/stop')
def stop_capture():
    global capturing
    capturing = False
    return "Sniffing stopped"


@app.route('/packets')
def get_packets():
    with capture_lock:
        return jsonify(packets)


@app.route('/graph')
def get_graph_data():
    with capture_lock:
        return jsonify({
            "timestamps": timestamps,
            "packet_counts": packet_counts
        })


@app.route('/export')
def export_packets():
    filename = "packets.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Time", "Source", "Destination", "Protocol", "Length"])
        for pkt in packets:
            writer.writerow([pkt["time"], pkt["source"], pkt["destination"], pkt["protocol"], pkt["length"]])
    return send_file(filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
