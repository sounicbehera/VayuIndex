// written by sounic behera
import React, { useEffect, useState } from "react";

interface FlightQuote {
  id: number;
  recorded_at: string;
  source_platform: string;
  carrier: string;
  flight_number: string;
  corridor_code: string;
  advance_window: string;
  departure_date: string;
  departure_time: string;
  base_fare: number;
  fuel_surcharge: number;
  tax_fees: number;
  total_fare: number;
  sha256_proof: string;
  proof_object_key: string;
}

interface ProofModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ProofOfDocumentModal({ isOpen, onClose }: ProofModalProps) {
  const [quotes, setQuotes] = useState<FlightQuote[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      fetch("http://127.0.0.1:8000/api/v1/quotes/latest?limit=50")
        .then((res) => res.json())
        .then((res) => {
          if (res.status === "success") {
            setQuotes(res.data);
          }
          setLoading(false);
        })
        .catch((err) => {
          console.error("Failed to load audit trail:", err);
          setLoading(false);
        });
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const latestQuote = quotes[0];
  const activeHash = latestQuote?.sha256_proof || "N/A";
  const activeS3Key = latestQuote?.proof_object_key || "N/A";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="relative w-full max-w-5xl rounded-xl border border-zinc-800 bg-zinc-950 p-6 text-zinc-100 shadow-2xl">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-4">
          <div>
            <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              <span className="h-3 w-3 rounded-full bg-emerald-500 animate-pulse" />
              Proof of Document & CCTV Audit Vault
            </h2>
            <p className="text-xs text-zinc-400 mt-1">
              Cryptographic SHA-256 Non-Repudiation WORM Verification
            </p>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-1.5 text-xs text-zinc-300 hover:bg-zinc-800"
          >
            Close ✕
          </button>
        </div>

        {/* Cryptographic Hash Bar */}
        <div className="my-4 rounded-lg bg-zinc-900/80 p-3 border border-zinc-800 text-xs font-mono">
          <div className="flex flex-col gap-1">
            <div className="flex items-center justify-between">
              <span className="text-zinc-500">ACTIVE BATCH SHA-256 PROOF:</span>
              <span className="text-emerald-400 font-semibold truncate max-w-[650px]">
                {activeHash}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-zinc-500">MINIO WORM S3 KEY:</span>
              <span className="text-zinc-300 truncate max-w-[650px]">{activeS3Key}</span>
            </div>
          </div>
        </div>

        {/* Flight Record Stream */}
        <div className="max-h-[480px] overflow-y-auto space-y-2 pr-2">
          {loading ? (
            <div className="py-12 text-center text-zinc-500">Loading immutable audit trail...</div>
          ) : quotes.length === 0 ? (
            <div className="py-12 text-center text-zinc-500">No flight records found.</div>
          ) : (
            quotes.map((q) => (
              <div
                key={q.id}
                className="flex items-center justify-between rounded-lg border border-zinc-800/80 bg-zinc-900/40 p-3 hover:border-zinc-700"
              >
                <div className="flex items-center gap-3">
                  <div className="flex flex-col gap-1.5 items-center">
                    <span className="rounded bg-indigo-500/10 px-2 py-1 text-xs font-medium text-indigo-400 border border-indigo-500/20">
                      {q.carrier}
                    </span>
                    {q.source_platform && (
                       <span className="rounded bg-sky-500/10 px-1.5 py-0.5 text-[9px] font-bold text-sky-400 border border-sky-500/20 uppercase tracking-widest text-center">
                         {q.source_platform.replace('_', ' ')}
                       </span>
                    )}
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-zinc-100">
                      {q.flight_number} • {q.corridor_code}
                    </div>
                    <div className="text-xs text-zinc-500">
                      Dep: {q.departure_date} at {q.departure_time} | Window: {q.advance_window}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-6 text-right">
                  <div>
                    <div className="text-xs text-zinc-400">
                      Base: ₹{q.base_fare} | YQ: ₹{q.fuel_surcharge} | Tax: ₹{q.tax_fees}
                    </div>
                    <div className="text-sm font-bold text-emerald-400">
                      ₹{q.total_fare.toLocaleString("en-IN")}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
