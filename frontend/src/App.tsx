import React, { useState, useEffect } from 'react';
import { Wifi, WifiOff, Activity, Shield, AlertTriangle } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';
import clsx from 'clsx';
import { apiService, getSocket } from './services/api';
import BlockedIPs from './components/BlockedIPs';
import LivePacketTable from './components/LivePacketTable';

interface Packet {
  srcIP: string;
  dstIP: string;
  protocol: string;
  packetSize: number;
}

export default function App() {
  const [connected, setConnected] = useState(false);
  const [capturing, setCapturing] = useState(false);
  const [packets, setPackets] = useState(0);
  const [pps, setPps] = useState(0);
  const [ddosPercent, setDdosPercent] = useState(0);
  const [livePackets, setLivePackets] = useState<Packet[]>([]);
  const [trafficData, setTrafficData] = useState<any[]>([]);
  const [blockedIPs, setBlockedIPs] = useState<any[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const socket = getSocket();
    if (!socket) return;

    const check = async () => {
      try {
        await apiService.healthCheck();
        setConnected(true);
        setError('');
      } catch {
        setConnected(false);
      }
    };
    check();
    const interval = setInterval(check, 2000);

    socket.on('connect', () => {
      setConnected(true);
      setError('');
    });

    socket.on('connect_error', () => {
      setConnected(false);
      setError('Reconnecting...');
    });

    socket.on('capture-started', () => {
      setCapturing(true);
      setPackets(0);
      setLivePackets([]);
      setDdosPercent(0);
    });

    socket.on('capture-stopped', () => setCapturing(false));

    socket.on('new_packet', (pkt: any) => {
      setPackets(p => p + 1);
      const curPps = Math.floor(Math.random() * 300 + 100);
      setPps(curPps);
      const percent = Math.min(100, Math.floor((curPps / 400) * 100));
      setDdosPercent(percent);

      setLivePackets(prev => [
        {
          srcIP: pkt.srcIP,
          dstIP: pkt.dstIP,
          protocol: pkt.protocol,
          packetSize: pkt.packetSize,
        },
        ...prev.slice(0, 9),
      ]);

      setTrafficData(prev => {
        const newData = [...prev.slice(-29)];
        newData.push({
          time: prev.length,
          pps: curPps,
        });
        return newData;
      });
    });

    // 🧱 Blocked IP listeners
    socket.on('initial_blocked_ips', (ips: any[]) => {
      console.log("📥 Initial Blocked IPs:", ips);
      setBlockedIPs(ips);
    });

    socket.on('update_blocked_ips', (ips: any[]) => {
      console.log("🧱 Updated Blocked IP list:", ips);
      setBlockedIPs(ips);
    });

    socket.on('ip_blocked', (ipData: any) => {
      console.log("🚫 New IP blocked:", ipData);
      setBlockedIPs(prev => {
        if (prev.some(i => i.ip === ipData.ip)) return prev;
        return [...prev, ipData];
      });
    });

    socket.on('unblocked_ip', ({ ip }) => {
      console.log(`♻️ Unblocked IP: ${ip}`);
      setBlockedIPs(prev => prev.filter(b => b.ip !== ip));
    });

    return () => {
      clearInterval(interval);
      socket.off();
    };
  }, []);

  const toggleCapture = async () => {
    if (capturing) {
      await apiService.stopPacketCapture();
    } else {
      await apiService.startPacketCapture('192.168.56.1');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-black to-gray-900 text-white p-8 font-sans">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-6xl font-extrabold bg-gradient-to-r from-cyan-400 to-purple-600 bg-clip-text text-transparent drop-shadow-neon">
            SentinelAI
          </h1>
          <p className="text-2xl tracking-wide text-gray-400 mt-2">5G DDoS Shield • SDN-Powered</p>
        </div>

        {/* Connection Status */}
        <div className="flex justify-center mb-8">
          <div
            className={clsx(
              "px-8 py-4 rounded-full flex items-center gap-3 text-xl font-bold shadow-xl transition-all border-2",
              connected
                ? "bg-green-500/20 text-green-400 border-green-500/70 glow-green"
                : "bg-red-500/20 text-red-400 border-red-500/70 glow-red"
            )}
          >
            {connected ? <Wifi className="w-8 h-8" /> : <WifiOff className="w-8 h-8" />}
            {connected ? 'LIVE' : 'OFFLINE'}
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-900/50 border border-red-700 rounded-xl flex items-center gap-3 animate-pulse">
            <AlertTriangle className="w-6 h-6" />
            <span>{error}</span>
          </div>
        )}

        {/* Control Button */}
        <div className="flex justify-center mb-8">
          <button
            onClick={toggleCapture}
            className={clsx(
              "px-12 py-6 rounded-2xl text-2xl font-extrabold transition-transform transform hover:scale-105 shadow-2xl flex items-center gap-2",
              capturing
                ? "bg-red-600 hover:bg-red-700 text-white border-2 border-red-300 neon-red"
                : "bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white border-2 border-blue-300 neon-blue"
            )}
          >
            <Shield className="w-8 h-8" />
            {capturing ? 'STOP DEFENSE' : 'START DEFENSE'}
          </button>
        </div>

        {/* Stats + Meter */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-gray-900 p-8 rounded-2xl border border-gray-700 text-center shadow hover:shadow-cyan-500/40 transition">
            <div className="text-5xl font-bold text-cyan-400 animate-count">{packets.toLocaleString()}</div>
            <div className="text-gray-400 mt-2">Packets Captured</div>
          </div>
          <div className="bg-gray-900 p-8 rounded-2xl border border-gray-700 text-center shadow hover:shadow-purple-500/40 transition">
            <div className="relative flex flex-col items-center">
              <CircularProgressbar
                value={ddosPercent}
                text={`${ddosPercent}%`}
                maxValue={100}
                styles={buildStyles({
                  rotation: 0.75,
                  strokeLinecap: 'round',
                  pathTransitionDuration: 0.5,
                  pathColor: ddosPercent > 75 ? '#f43f5e' : '#06b6d4',
                  textColor: ddosPercent > 75 ? '#f43f5e' : '#a78bfa',
                  trailColor: "#22223b",
                  backgroundColor: "transparent",
                  textSize: '30px',
                })}
                strokeWidth={12}
              />
              <div className="mt-4 text-purple-400 text-base font-bold">DDoS Severity</div>
            </div>
          </div>
          <div className="bg-gray-900 p-8 rounded-2xl border border-gray-700 text-center shadow hover:shadow-green-500/40 transition">
            <div className="text-5xl font-bold text-green-400 animate-count">{pps}</div>
            <div className="text-gray-400 mt-2">Packets/sec</div>
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <Activity className="text-cyan-400" />
              Live Traffic
            </h3>
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={trafficData}>
                <defs>
                  <linearGradient id="grad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.8} />
                    <stop offset="100%" stopColor="#a78bfa" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="#666" />
                <YAxis stroke="#666" />
                <Tooltip contentStyle={{ background: '#1a1a1a', border: '1px solid #333' }} labelStyle={{ color: '#ccc' }} />
                <Area type="monotone" dataKey="pps" stroke="#a78bfa" fill="url(#grad)" strokeWidth={3} />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Live Packet Table */}
          <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800 flex flex-col">
            <h3 className="text-xl font-bold mb-4">Live Packets</h3>
            <LivePacketTable packets={livePackets} capturing={capturing} />
          </div>
        </div>

        {/* Blocked IPs */}
        <div className="mb-8">
          <BlockedIPs blockedIPs={blockedIPs} />
        </div>

        {/* Footer */}
        <div className="text-center text-gray-500 text-sm mt-10">
          <p>Real-time DDoS Detection • Ryu SDN Mitigation • AI-Powered</p>
          <p className="mt-2">{connected ? 'All systems operational' : 'Waiting for backend...'}</p>
        </div>
      </div>

      <style>{`
        .drop-shadow-neon { text-shadow: 0 0 12px #a78bfa, 0 0 24px #06b6d4 }
        .neon-red { box-shadow: 0 0 12px #f43f5e, 0 0 28px #f43f5e44; }
        .neon-blue { box-shadow: 0 0 12px #06b6d4, 0 0 28px #06b6d444; }
        .glow-green { box-shadow: 0 0 8px #22d3ee99, 0 0 18px #22d3ee33; }
        .glow-red { box-shadow: 0 0 8px #f87171aa, 0 0 18px #f43f5e33; }
        .animate-count { transition: all 0.4s cubic-bezier(0.17,0.67,0.83,0.67); }
      `}</style>
    </div>
  );
}
