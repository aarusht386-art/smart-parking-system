"""
SMARTPARK 360
College Smart Parking System
Single-file Python web application.

Run:
    python smartpark360.py
Then open:
    http://127.0.0.1:8000
"""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from datetime import datetime
import json
import random
import string

HOST = "127.0.0.1"
PORT = 8000

PARKING_SLOTS = [
    {"id": "G01", "floor": "Ground", "type": "Car", "status": "Available", "vehicle": ""},
    {"id": "G02", "floor": "Ground", "type": "Car", "status": "Occupied", "vehicle": "MP20AB1234"},
    {"id": "G03", "floor": "Ground", "type": "Car", "status": "Available", "vehicle": ""},
    {"id": "G04", "floor": "Ground", "type": "Bike", "status": "Available", "vehicle": ""},
    {"id": "G05", "floor": "Ground", "type": "Car", "status": "Occupied", "vehicle": "MP51CD5678"},
    {"id": "G06", "floor": "Ground", "type": "Bike", "status": "Available", "vehicle": ""},
    {"id": "F01", "floor": "First", "type": "Car", "status": "Available", "vehicle": ""},
    {"id": "F02", "floor": "First", "type": "Car", "status": "Reserved", "vehicle": "MP20EF1111"},
    {"id": "F03", "floor": "First", "type": "Car", "status": "Available", "vehicle": ""},
    {"id": "F04", "floor": "First", "type": "Bike", "status": "Available", "vehicle": ""},
    {"id": "F05", "floor": "First", "type": "Car", "status": "Occupied", "vehicle": "MP20GH2222"},
    {"id": "F06", "floor": "First", "type": "Bike", "status": "Available", "vehicle": ""},
    {"id": "F07", "floor": "First", "type": "Car", "status": "Available", "vehicle": ""},
    {"id": "F08", "floor": "First", "type": "Car", "status": "Available", "vehicle": ""},
]

BOOKINGS = [{
    "id": "BK1001", "name": "Demo User", "vehicle": "MP20EF1111",
    "slot": "F02", "date": "2026-09-14", "time": "18:00", "status": "Confirmed"
}]

ACTIVITY = [
    {"time": "11:10", "message": "Vehicle MP20GH2222 entered F05", "kind": "entry"},
    {"time": "10:30", "message": "Vehicle MP51CD5678 entered G05", "kind": "entry"},
    {"time": "09:15", "message": "Vehicle MP20AB1234 entered G02", "kind": "entry"},
    {"time": "08:55", "message": "Booking BK1001 confirmed for F02", "kind": "booking"},
]


def get_slot(slot_id):
    return next((s for s in PARKING_SLOTS if s["id"] == slot_id.upper()), None)


def add_activity(message, kind):
    ACTIVITY.insert(0, {
        "time": datetime.now().strftime("%H:%M"),
        "message": message,
        "kind": kind,
    })


def make_booking_id():
    return "BK" + "".join(random.choices(string.digits, k=4))


def get_state():
    total = len(PARKING_SLOTS)
    available = sum(s["status"] == "Available" for s in PARKING_SLOTS)
    occupied = sum(s["status"] == "Occupied" for s in PARKING_SLOTS)
    reserved = sum(s["status"] == "Reserved" for s in PARKING_SLOTS)
    return {
        "slots": PARKING_SLOTS,
        "bookings": BOOKINGS,
        "activity": ACTIVITY[:12],
        "stats": {
            "total": total,
            "available": available,
            "occupied": occupied,
            "reserved": reserved,
            "occupancy": round(((occupied + reserved) / total) * 100),
        },
    }


HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SmartPark 360 | Smart Parking</title>
<style>
:root{--bg:#07111f;--bg2:#0b1728;--panel:#101e31;--panel2:#14243a;--text:#f7fbff;--muted:#91a2b7;--line:rgba(255,255,255,.09);--cyan:#22d3ee;--blue:#3b82f6;--green:#22c55e;--yellow:#f59e0b;--red:#ef4444;--shadow:0 20px 60px rgba(0,0,0,.28)}
*{box-sizing:border-box;scroll-behavior:smooth}body{margin:0;font-family:Inter,Segoe UI,Arial,sans-serif;background:var(--bg);color:var(--text)}
a{text-decoration:none;color:inherit}button,input,select{font:inherit}button{cursor:pointer}
.navbar{position:fixed;top:0;left:0;right:0;z-index:100;height:76px;display:flex;align-items:center;justify-content:space-between;padding:0 6%;background:rgba(7,17,31,.82);backdrop-filter:blur(16px);border-bottom:1px solid var(--line)}
.logo{display:flex;align-items:center;gap:10px;font-size:21px;font-weight:900}.logo-mark{width:38px;height:38px;display:grid;place-items:center;border-radius:11px;background:linear-gradient(135deg,var(--cyan),var(--blue));color:#06101e}
.navlinks{display:flex;gap:28px;color:#c4d0df;font-size:14px}.navlinks a:hover{color:var(--cyan)}.nav-btn{padding:11px 17px;border-radius:10px;background:linear-gradient(135deg,var(--cyan),var(--blue));color:#06101e;font-weight:800}
.hero{min-height:760px;padding:150px 6% 80px;display:grid;grid-template-columns:1.05fr .95fr;gap:55px;align-items:center;position:relative;overflow:hidden}
.hero:before{content:"";position:absolute;width:600px;height:600px;right:-160px;top:80px;background:radial-gradient(circle,rgba(34,211,238,.18),transparent 68%)}
.eyebrow{display:inline-flex;align-items:center;gap:8px;padding:8px 12px;border:1px solid rgba(34,211,238,.25);background:rgba(34,211,238,.06);color:var(--cyan);border-radius:30px;font-size:12px;font-weight:800}
.hero h1{font-size:clamp(45px,6vw,78px);line-height:1.02;margin:22px 0;letter-spacing:-3px}.gradient{background:linear-gradient(90deg,#fff,#67e8f9,#60a5fa);-webkit-background-clip:text;background-clip:text;color:transparent}
.hero p{color:var(--muted);font-size:17px;line-height:1.8;max-width:650px}.hero-actions{display:flex;gap:12px;margin-top:28px;flex-wrap:wrap}
.primary{background:linear-gradient(135deg,var(--cyan),var(--blue));color:#06101e;border:0;padding:14px 20px;border-radius:11px;font-weight:900}
.secondary{background:rgba(255,255,255,.05);color:white;border:1px solid var(--line);padding:14px 20px;border-radius:11px;font-weight:800}
.hero-stats{display:flex;gap:30px;margin-top:40px;flex-wrap:wrap}.hero-stat b{font-size:25px}.hero-stat span{display:block;color:var(--muted);font-size:12px;margin-top:4px}
.dashboard-preview{background:linear-gradient(145deg,#11233a,#0a1525);border:1px solid rgba(255,255,255,.11);border-radius:22px;padding:18px;box-shadow:var(--shadow);transform:rotate(1deg)}
.preview-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px}.live{color:#86efac;font-size:11px;font-weight:800}.preview-title{font-size:13px;color:#cbd5e1}
.preview-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:9px}.preview-slot{aspect-ratio:1;border-radius:10px;display:grid;place-items:center;font-size:11px;font-weight:900;border:1px solid rgba(255,255,255,.06)}
.free{background:rgba(34,197,94,.12);color:#86efac}.busy{background:rgba(239,68,68,.12);color:#fca5a5}.reserve{background:rgba(245,158,11,.12);color:#fcd34d}
.preview-bottom{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:14px}.mini-stat{background:rgba(255,255,255,.04);padding:12px;border-radius:10px}.mini-stat span{display:block;color:var(--muted);font-size:10px}.mini-stat b{font-size:20px}
.section{padding:90px 6%}.section-head{max-width:700px;margin-bottom:42px}.kicker{color:var(--cyan);font-size:12px;font-weight:900;letter-spacing:1px;text-transform:uppercase}
.section h2{font-size:40px;letter-spacing:-1.5px;margin:10px 0 12px}.section-head p{color:var(--muted);line-height:1.7}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.feature{background:linear-gradient(145deg,rgba(255,255,255,.055),rgba(255,255,255,.025));border:1px solid var(--line);padding:26px;border-radius:18px;transition:.25s}
.feature:hover{transform:translateY(-5px);border-color:rgba(34,211,238,.3)}.feature-icon{width:48px;height:48px;display:grid;place-items:center;border-radius:13px;background:rgba(34,211,238,.1);font-size:22px}
.feature h3{margin:18px 0 9px}.feature p{color:var(--muted);line-height:1.65;font-size:14px}
.solutions{background:#091524;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}.solution-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.solution{padding:23px;min-height:180px;background:#0d1c2e;border:1px solid var(--line);border-radius:16px}.solution b{display:block;margin:13px 0 7px}.solution span{color:var(--muted);font-size:13px;line-height:1.55}
.live-section{background:#06101d}.parking-panel{background:#0d1b2c;border:1px solid var(--line);border-radius:20px;padding:22px}
.panel-head{display:flex;justify-content:space-between;align-items:center;gap:15px;margin-bottom:20px}.panel-head h3{margin:0}.live-badge{color:#86efac;font-size:11px;font-weight:900}
.dashboard-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:22px}.dstat{padding:17px;border-radius:13px;background:rgba(255,255,255,.035);border:1px solid var(--line)}
.dstat span{display:block;color:var(--muted);font-size:11px}.dstat b{font-size:27px;display:block;margin-top:5px}.dstat.available b{color:#86efac}.dstat.occupied b{color:#fca5a5}.dstat.reserved b{color:#fcd34d}
.toolbar{display:flex;gap:10px;margin-bottom:17px;flex-wrap:wrap}.toolbar input,.toolbar select,.form-input{background:#081525;color:white;border:1px solid var(--line);border-radius:9px;padding:11px 12px;outline:none}
.toolbar input{min-width:260px}.toolbar input:focus,.toolbar select:focus,.form-input:focus{border-color:var(--cyan)}
.slot-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:10px}.slot{min-height:105px;border-radius:12px;padding:12px;border:1px solid var(--line);background:#102239;position:relative}
.slot-id{font-weight:900;font-size:15px}.slot-status{position:absolute;top:10px;right:10px;width:8px;height:8px;border-radius:50%}
.slot-status.Available{background:var(--green);box-shadow:0 0 10px rgba(34,197,94,.6)}.slot-status.Occupied{background:var(--red)}.slot-status.Reserved{background:var(--yellow)}
.slot .vehicle{font-size:11px;color:#cbd5e1;margin-top:25px}.slot .type{font-size:10px;color:var(--muted);margin-top:4px}
.booking-area{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:18px}.form-card{background:#0d1b2c;border:1px solid var(--line);border-radius:18px;padding:23px}
.form-card h3{margin-top:0}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.form-group label{display:block;font-size:11px;color:var(--muted);margin-bottom:6px}.full{grid-column:1/-1}
.form-card .primary{width:100%;margin-top:13px}.booking-list{max-height:330px;overflow:auto}
.booking-row{display:grid;grid-template-columns:1fr 1fr 75px;gap:10px;padding:13px 0;border-bottom:1px solid var(--line);font-size:12px}.booking-row span{color:var(--muted)}.confirmed{color:#86efac!important}
.activity{display:flex;flex-direction:column;gap:12px;max-height:330px;overflow:auto}.activity-row{display:flex;gap:11px;padding:12px;background:rgba(255,255,255,.03);border-radius:10px}
.activity-icon{width:33px;height:33px;border-radius:9px;display:grid;place-items:center;background:rgba(34,211,238,.09)}.activity-row b{font-size:12px}.activity-row small{display:block;color:var(--muted);margin-top:4px}
.cta{margin:0 6% 80px;padding:55px;border-radius:25px;background:radial-gradient(circle at 85% 20%,rgba(34,211,238,.22),transparent 30%),linear-gradient(135deg,#102b44,#0b1728);border:1px solid var(--line);display:flex;justify-content:space-between;align-items:center;gap:25px}
.cta h2{font-size:34px;margin:0 0 8px}.cta p{color:var(--muted);margin:0;line-height:1.6}
footer{padding:30px 6%;border-top:1px solid var(--line);color:var(--muted);font-size:12px;display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap}
.modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:200;align-items:center;justify-content:center;padding:20px}.modal.show{display:flex}
.modal-box{width:min(520px,100%);background:#0d1b2c;border:1px solid var(--line);border-radius:18px;padding:25px;box-shadow:var(--shadow)}
.modal-head{display:flex;justify-content:space-between;align-items:center}.close{background:transparent;color:white;border:0;font-size:22px}
.message{display:none;margin-top:12px;padding:10px;border-radius:8px;font-size:12px}.message.ok{display:block;background:rgba(34,197,94,.12);color:#86efac}.message.err{display:block;background:rgba(239,68,68,.12);color:#fca5a5}
.muted{color:var(--muted)}
@media(max-width:1000px){.hero{grid-template-columns:1fr}.dashboard-preview{max-width:650px}.cards{grid-template-columns:1fr 1fr}.solution-grid{grid-template-columns:1fr 1fr}.slot-grid{grid-template-columns:repeat(4,1fr)}.booking-area{grid-template-columns:1fr}}
@media(max-width:700px){.navbar{padding:0 4%}.navlinks{display:none}.hero{padding:125px 5% 70px}.hero h1{letter-spacing:-2px}.section{padding:65px 5%}.cards,.solution-grid{grid-template-columns:1fr}.dashboard-stats{grid-template-columns:1fr 1fr}.slot-grid{grid-template-columns:repeat(2,1fr)}.form-grid{grid-template-columns:1fr}.full{grid-column:auto}.cta{margin:0 5% 55px;padding:32px;display:block}.cta .primary{margin-top:18px}}
</style>
</head>
<body>
<header class="navbar">
<a href="#" class="logo"><span class="logo-mark">P</span><span>SmartPark<span style="color:#22d3ee">360</span></span></a>
<nav class="navlinks"><a href="#solutions">Solutions</a><a href="#features">Features</a><a href="#live">Live Parking</a><a href="#booking">Booking</a></nav>
<a class="nav-btn" href="#live">View Parking</a>
</header>

<section class="hero">
<div>
<span class="eyebrow">● SMART PARKING MANAGEMENT</span>
<h1>Smarter parking.<br><span class="gradient">Smoother mobility.</span></h1>
<p>A modern parking management platform for real-time occupancy, digital reservations, vehicle entry and exit, and intelligent parking-space utilization.</p>
<div class="hero-actions"><a class="primary" href="#live">Explore Live Parking →</a><a class="secondary" href="#features">Explore Solutions</a></div>
<div class="hero-stats"><div class="hero-stat"><b>24/7</b><span>Parking monitoring</span></div><div class="hero-stat"><b>Real-time</b><span>Slot availability</span></div><div class="hero-stat"><b>100%</b><span>Digital management</span></div></div>
</div>
<div class="dashboard-preview">
<div class="preview-top"><div><div class="preview-title">SMARTPARK LIVE CONTROL</div><b>Parking Overview</b></div><div class="live">● LIVE</div></div>
<div class="preview-grid" id="previewGrid"></div>
<div class="preview-bottom"><div class="mini-stat"><span>Available</span><b id="previewAvailable">0</b></div><div class="mini-stat"><span>Occupied</span><b id="previewOccupied">0</b></div><div class="mini-stat"><span>Occupancy</span><b id="previewOccupancy">0%</b></div></div>
</div>
</section>

<section class="section solutions" id="solutions">
<div class="section-head"><div class="kicker">Solutions</div><h2>One platform for the complete parking journey.</h2><p>From vehicle arrival to parking allocation and exit, SmartPark 360 brings the essential parking operations together in one simple interface.</p></div>
<div class="solution-grid">
<div class="solution"><div>🚗</div><b>Parking Management</b><span>Monitor parking spaces and manage occupied, available and reserved slots.</span></div>
<div class="solution"><div>📡</div><b>Real-Time Monitoring</b><span>See live parking occupancy and quickly identify available spaces.</span></div>
<div class="solution"><div>📅</div><b>Digital Booking</b><span>Reserve a parking slot before arrival and reduce unnecessary waiting.</span></div>
<div class="solution"><div>🔐</div><b>Access Management</b><span>Record vehicle entry and exit with a simple digital workflow.</span></div>
</div>
</section>

<section class="section" id="features">
<div class="section-head"><div class="kicker">Powerful Features</div><h2>Designed around the modern parking experience.</h2><p>This college-project implementation focuses on the core ideas used by professional parking-management platforms: visibility, automation and convenience.</p></div>
<div class="cards">
<div class="feature"><div class="feature-icon">📊</div><h3>Live Dashboard</h3><p>Get an instant view of total capacity, available spaces, occupancy and reservations.</p></div>
<div class="feature"><div class="feature-icon">🅿️</div><h3>Smart Slot Detection</h3><p>Every slot has a clear state so users can quickly identify where a vehicle can be parked.</p></div>
<div class="feature"><div class="feature-icon">🚘</div><h3>Vehicle Entry & Exit</h3><p>Register vehicle entry and automatically release its parking space during exit.</p></div>
<div class="feature"><div class="feature-icon">📅</div><h3>Advance Booking</h3><p>Reserve an available slot with customer, vehicle, date and time information.</p></div>
<div class="feature"><div class="feature-icon">🧾</div><h3>Activity History</h3><p>Keep a simple activity trail of entries, exits and parking reservations.</p></div>
<div class="feature"><div class="feature-icon">📱</div><h3>Responsive UI</h3><p>The interface adapts to desktop and mobile-sized screens for easier demonstrations.</p></div>
</div>
</section>

<section class="section live-section" id="live">
<div class="section-head"><div class="kicker">Live Parking</div><h2>Real-time parking control.</h2><p>Use the controls below to demonstrate your complete parking workflow.</p></div>
<div class="parking-panel">
<div class="panel-head"><div><h3>Parking Occupancy</h3><span class="muted">All floors • SmartPark 360</span></div><span class="live-badge">● SYSTEM ONLINE</span></div>
<div class="dashboard-stats"><div class="dstat"><span>Total Slots</span><b id="total">0</b></div><div class="dstat available"><span>Available</span><b id="available">0</b></div><div class="dstat occupied"><span>Occupied</span><b id="occupied">0</b></div><div class="dstat reserved"><span>Reserved</span><b id="reserved">0</b></div></div>
<div class="toolbar"><input id="search" placeholder="Search slot / vehicle..." oninput="renderSlots()"><select id="floor" onchange="renderSlots()"><option value="All">All Floors</option><option value="Ground">Ground Floor</option><option value="First">First Floor</option></select><button class="secondary" onclick="loadState()">↻ Refresh</button></div>
<div class="slot-grid" id="slotGrid"></div>
</div>

<div class="booking-area" id="booking">
<div class="form-card"><h3>📅 Reserve a Parking Slot</h3><p class="muted">Create a quick demo booking.</p>
<div class="form-grid">
<div class="form-group"><label>Customer Name</label><input class="form-input" id="customerName" placeholder="Enter name"></div>
<div class="form-group"><label>Vehicle Number</label><input class="form-input" id="bookingVehicle" placeholder="MP20AB1234"></div>
<div class="form-group"><label>Vehicle Type</label><select class="form-input" id="bookingType"><option>Car</option><option>Bike</option></select></div>
<div class="form-group"><label>Available Slot</label><select class="form-input" id="bookingSlot"></select></div>
<div class="form-group"><label>Date</label><input class="form-input" id="bookingDate" type="date"></div>
<div class="form-group"><label>Time</label><input class="form-input" id="bookingTime" type="time" value="18:00"></div>
</div><button class="primary" onclick="createBooking()">Confirm Booking</button><div id="bookingMessage" class="message"></div>
</div>

<div class="form-card"><h3>🚗 Vehicle Entry / Exit</h3><p class="muted">Demonstrate the parking movement workflow.</p>
<div class="form-grid"><div class="form-group full"><label>Vehicle Number</label><input class="form-input" id="vehicleNumber" placeholder="MP20XY9876"></div>
<div class="form-group"><label>Vehicle Type</label><select class="form-input" id="vehicleType"><option>Car</option><option>Bike</option></select></div>
<div class="form-group"><label>Parking Slot</label><select class="form-input" id="entrySlot"></select></div></div>
<div style="display:flex;gap:10px;margin-top:13px"><button class="primary" onclick="vehicleEntry()">Vehicle Entry</button><button class="secondary" onclick="vehicleExit()">Vehicle Exit</button></div><div id="entryMessage" class="message"></div>
</div>
</div>

<div class="booking-area"><div class="form-card"><h3>📋 Current Reservations</h3><div id="bookingList" class="booking-list"></div></div><div class="form-card"><h3>⚡ Recent Activity</h3><div id="activity" class="activity"></div></div></div>
</section>

<section class="cta"><div><h2>Make parking smarter.</h2><p>A complete college-level smart parking demonstration built in Python.</p></div><a href="#live" class="primary">Open Live System →</a></section>
<footer><span>© 2026 SmartPark 360 • College Smart Parking Project</span><span>Python • HTML • CSS • JavaScript • No external packages</span></footer>
<div class="modal" id="slotModal"><div class="modal-box"><div class="modal-head"><h3 id="modalTitle">Parking Slot</h3><button class="close" onclick="closeModal()">×</button></div><div id="modalBody" class="muted" style="line-height:1.7;margin-top:15px"></div></div></div>

<script>
let DATA = {slots:[], bookings:[], activity:[], stats:{}};
const $ = id => document.getElementById(id);

async function loadState(){
    try {
        const response = await fetch('/api/state');
        DATA = await response.json();
        renderAll();
    } catch (error) {
        console.error(error);
    }
}
function renderAll(){
    const s = DATA.stats;
    $('total').textContent=s.total; $('available').textContent=s.available;
    $('occupied').textContent=s.occupied; $('reserved').textContent=s.reserved;
    $('previewAvailable').textContent=s.available; $('previewOccupied').textContent=s.occupied;
    $('previewOccupancy').textContent=s.occupancy+'%';
    renderPreview(); renderSlots(); renderBookingOptions(); renderBookings(); renderActivity();
}
function renderPreview(){
    $('previewGrid').innerHTML=DATA.slots.map(slot=>{
        const cls=slot.status==='Available'?'free':slot.status==='Occupied'?'busy':'reserve';
        return `<div class="preview-slot ${cls}">${slot.id}</div>`;
    }).join('');
}
function renderSlots(){
    const query=($('search').value||'').toLowerCase(), floor=$('floor').value;
    const filtered=DATA.slots.filter(slot=>{
        const matchesFloor=floor==='All'||slot.floor===floor;
        const matchesSearch=!query||slot.id.toLowerCase().includes(query)||(slot.vehicle||'').toLowerCase().includes(query);
        return matchesFloor&&matchesSearch;
    });
    $('slotGrid').innerHTML=filtered.map(slot=>`
        <div class="slot" onclick="showSlot('${slot.id}')">
            <span class="slot-id">${slot.id}</span><span class="slot-status ${slot.status}"></span>
            <div class="vehicle">${slot.vehicle|| (slot.status==='Available'?'Available':'Reserved')}</div>
            <div class="type">${slot.floor} • ${slot.type}</div>
        </div>`).join('');
}
function renderBookingOptions(){
    const available=DATA.slots.filter(s=>s.status==='Available');
    $('bookingSlot').innerHTML=available.length?available.map(s=>`<option value="${s.id}">${s.id} — ${s.floor} — ${s.type}</option>`).join(''):'<option value="">No slots available</option>';
    $('entrySlot').innerHTML=available.length?available.map(s=>`<option value="${s.id}">${s.id} — ${s.floor} — ${s.type}</option>`).join(''):'<option value="">No slots available</option>';
}
function renderBookings(){
    if(!DATA.bookings.length){$('bookingList').innerHTML='<div class="muted">No bookings yet.</div>';return;}
    $('bookingList').innerHTML=DATA.bookings.map(b=>`
        <div class="booking-row"><div><b>${b.name}</b><br><span>${b.vehicle}</span></div>
        <div><b>${b.slot}</b><br><span>${b.date} • ${b.time}</span></div><div class="confirmed">${b.status}</div></div>`).join('');
}
function renderActivity(){
    $('activity').innerHTML=DATA.activity.map(a=>`
        <div class="activity-row"><div class="activity-icon">${a.kind==='entry'?'🚗':a.kind==='exit'?'🚪':'📅'}</div>
        <div><b>${a.message}</b><small>${a.time}</small></div></div>`).join('');
}
function showSlot(id){
    const slot=DATA.slots.find(s=>s.id===id); if(!slot)return;
    $('modalTitle').textContent=`Parking Slot ${slot.id}`;
    $('modalBody').innerHTML=`<b>Status:</b> ${slot.status}<br><b>Floor:</b> ${slot.floor}<br><b>Vehicle Type:</b> ${slot.type}<br><b>Vehicle:</b> ${slot.vehicle||'None'}<br><br>${slot.status==='Available'?'<span style="color:#86efac">This slot is available for parking.</span>':'<span>This slot is currently not available.</span>'}`;
    $('slotModal').classList.add('show');
}
function closeModal(){$('slotModal').classList.remove('show');}
async function postData(url,data,messageId){
    try{
        const response=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
        const result=await response.json(),box=$(messageId);
        if(!response.ok||result.error){box.textContent=result.error||'Something went wrong.';box.className='message err';return;}
        DATA=result;renderAll();box.textContent='Operation completed successfully!';box.className='message ok';
    }catch(error){const box=$(messageId);box.textContent='Could not connect to the server.';box.className='message err';}
}
function createBooking(){
    const data={name:$('customerName').value.trim(),vehicle:$('bookingVehicle').value.trim().toUpperCase(),type:$('bookingType').value,slot:$('bookingSlot').value,date:$('bookingDate').value,time:$('bookingTime').value};
    if(!data.name||!data.vehicle||!data.slot||!data.date||!data.time){$('bookingMessage').textContent='Please fill all booking fields.';$('bookingMessage').className='message err';return;}
    postData('/api/book',data,'bookingMessage');
}
function vehicleEntry(){
    const data={vehicle:$('vehicleNumber').value.trim().toUpperCase(),type:$('vehicleType').value,slot:$('entrySlot').value};
    if(!data.vehicle){$('entryMessage').textContent='Enter a vehicle number.';$('entryMessage').className='message err';return;}
    postData('/api/entry',data,'entryMessage');
}
function vehicleExit(){
    const vehicle=$('vehicleNumber').value.trim().toUpperCase();
    if(!vehicle){$('entryMessage').textContent='Enter the vehicle number for exit.';$('entryMessage').className='message err';return;}
    postData('/api/exit',{vehicle},'entryMessage');
}
$('bookingDate').value=new Date().toISOString().slice(0,10);
loadState();setInterval(loadState,10000);
</script>
</body>
</html>
"""


class SmartParkHandler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            return {}

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            body = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/api/state":
            self.send_json(get_state())
        else:
            self.send_json({"error": "Page not found"}, 404)

    def do_POST(self):
        path = urlparse(self.path).path
        data = self.read_json()

        if path == "/api/entry":
            vehicle = str(data.get("vehicle", "")).strip().upper()
            slot_id = str(data.get("slot", "")).strip().upper()
            vehicle_type = str(data.get("type", "Car"))
            slot = get_slot(slot_id)
            if not vehicle or not slot:
                return self.send_json({"error": "Vehicle number and valid slot are required."}, 400)
            if any(s["vehicle"] == vehicle for s in PARKING_SLOTS):
                return self.send_json({"error": "This vehicle is already inside the parking area."}, 400)
            if slot["status"] != "Available":
                return self.send_json({"error": f"Slot {slot_id} is not available."}, 400)
            if slot["type"] != vehicle_type:
                return self.send_json({"error": f"Slot {slot_id} is for {slot['type']} vehicles."}, 400)
            slot["status"], slot["vehicle"] = "Occupied", vehicle
            add_activity(f"Vehicle {vehicle} entered {slot_id}", "entry")
            return self.send_json(get_state())

        if path == "/api/exit":
            vehicle = str(data.get("vehicle", "")).strip().upper()
            slot = next((s for s in PARKING_SLOTS if s["vehicle"] == vehicle), None)
            if not slot:
                return self.send_json({"error": "Vehicle was not found in the parking area."}, 404)
            slot_id = slot["id"]
            slot["status"], slot["vehicle"] = "Available", ""
            for booking in BOOKINGS:
                if booking["vehicle"] == vehicle and booking["slot"] == slot_id and booking["status"] == "Confirmed":
                    booking["status"] = "Completed"
            add_activity(f"Vehicle {vehicle} exited {slot_id}", "exit")
            return self.send_json(get_state())

        if path == "/api/book":
            name = str(data.get("name", "")).strip()
            vehicle = str(data.get("vehicle", "")).strip().upper()
            vehicle_type = str(data.get("type", "Car"))
            slot_id = str(data.get("slot", "")).strip().upper()
            date = str(data.get("date", "")).strip()
            time = str(data.get("time", "")).strip()
            if not all([name, vehicle, slot_id, date, time]):
                return self.send_json({"error": "Please fill all booking fields."}, 400)
            slot = get_slot(slot_id)
            if not slot:
                return self.send_json({"error": "Selected slot does not exist."}, 400)
            if slot["status"] != "Available":
                return self.send_json({"error": "Selected slot is no longer available."}, 400)
            if slot["type"] != vehicle_type:
                return self.send_json({"error": f"Slot {slot_id} is for {slot['type']} vehicles."}, 400)
            if any(s["vehicle"] == vehicle for s in PARKING_SLOTS):
                return self.send_json({"error": "This vehicle is already inside the parking area."}, 400)
            booking_id = make_booking_id()
            BOOKINGS.insert(0, {
                "id": booking_id, "name": name, "vehicle": vehicle, "slot": slot_id,
                "date": date, "time": time, "status": "Confirmed",
            })
            slot["status"], slot["vehicle"] = "Reserved", vehicle
            add_activity(f"Booking {booking_id} confirmed for {slot_id}", "booking")
            return self.send_json(get_state())

        return self.send_json({"error": "Endpoint not found"}, 404)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print("\n" + "=" * 58)
    print("        SMARTPARK 360 - SMART PARKING SYSTEM")
    print("=" * 58)
    print(f"Open in Chrome: http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop the application.")
    print("=" * 58 + "\n")
    server = ThreadingHTTPServer((HOST, PORT), SmartParkHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSmartPark 360 stopped.")
    finally:
        server.server_close()
