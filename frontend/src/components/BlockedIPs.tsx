import React from 'react';
import { Shield, Unlock } from 'lucide-react';

interface BlockedIP {
  ip: string;
  timestamp: string;
  reason: string;
  threatLevel: 'high' | 'medium' | 'low';
  mitigation?: string;
}

export default function BlockedIPs({ blockedIPs = [] }: { blockedIPs: BlockedIP[] }) {
  const unblock = async (ip: string) => {
    await fetch('http://localhost:3000/api/unblock', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ip }),
    });
  };

  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
      <div className="p-4 bg-gradient-to-r from-red-900/50 to-purple-900/50 border-b border-gray-800">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <Shield className="w-5 h-5 text-red-400" />
          Blocked Attackers ({blockedIPs.length})
        </h3>
      </div>

      {blockedIPs.length === 0 ? (
        <div className="p-12 text-center">
          <Shield className="w-16 h-16 mx-auto mb-4 text-gray-700" />
          <p className="text-gray-400">No threats blocked</p>
          <p className="text-sm text-gray-500 mt-2">System is secure</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-xs text-gray-500 border-b border-gray-800">
                <th className="px-4 py-3">IP Address</th>
                <th className="px-4 py-3">Threat</th>
                <th className="px-4 py-3">Reason</th>
                <th className="px-4 py-3">Time</th>
                <th className="px-4 py-3">Action</th>
              </tr>
            </thead>
            <tbody>
              {blockedIPs.map((item) => (
                <tr key={item.ip} className="border-b border-gray-800 hover:bg-gray-800/50 transition-colors">
                  <td className="px-4 py-3 font-mono text-red-400 text-sm">{item.ip}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-1 rounded text-xs font-bold ${
                        item.threatLevel === 'high'
                          ? 'bg-red-600 text-white'
                          : item.threatLevel === 'medium'
                          ? 'bg-orange-500 text-white'
                          : 'bg-yellow-600 text-black'
                      }`}
                    >
                      {item.threatLevel.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-300 text-sm max-w-xs truncate">
                    {item.reason || 'DDoS Flood'}
                  </td>
                  <td className="px-4 py-3 text-gray-400 text-xs">
                    {new Date(item.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => unblock(item.ip)}
                      className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 rounded text-xs transition-colors"
                    >
                      <Unlock className="w-3 h-3" />
                      Unblock
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
