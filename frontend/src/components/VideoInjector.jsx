import React, { useState, useEffect, useRef } from 'react';
import { Upload, Video, Play, RefreshCw, CheckCircle2, Film, AlertTriangle, FileVideo, Shield, ArrowRight } from 'lucide-react';
import { uploadCustomVideo, fetchUploadedVideos, injectVideoToBay, resetBayVideo, processCustomVideoOffline } from '../services/api';

export default function VideoInjector({ selectedBayId, onVideoInjected }) {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [activeCategory, setActiveCategory] = useState('Electronics & Fragile');
  const [targetBay, setTargetBay] = useState(selectedBayId || 'BAY-01');
  const [statusMsg, setStatusMsg] = useState(null);
  const [scanSummary, setScanSummary] = useState(null);
  const fileInputRef = useRef(null);

  const categories = [
    'Electronics & Fragile',
    'Glassware & Ceramics',
    'Heavy Industrial Goods',
    'Perishables & Cold Chain',
    'General Boxed Cargo'
  ];

  const bays = ['BAY-01', 'BAY-02', 'BAY-03', 'BAY-04'];

  const loadUploadedList = async () => {
    try {
      const list = await fetchUploadedVideos();
      setUploadedFiles(list || []);
      if (list && list.length > 0 && !selectedFile) {
        setSelectedFile(list[0].filename);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadUploadedList();
  }, []);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setStatusMsg(`Uploading ${file.name}...`);
    try {
      const res = await uploadCustomVideo(file);
      setStatusMsg(`Uploaded ${res.original_name} successfully!`);
      await loadUploadedList();
      setSelectedFile(res.filename);
    } catch (err) {
      alert('Upload failed: ' + err.message);
      setStatusMsg(null);
    } finally {
      setUploading(false);
    }
  };

  const handleStreamVideo = async () => {
    if (!selectedFile) return;
    setStatusMsg(`Injecting ${selectedFile} into ${targetBay}...`);
    try {
      await injectVideoToBay(targetBay, selectedFile);
      setStatusMsg(`✅ ${selectedFile} is now actively streaming into ${targetBay}!`);
      if (onVideoInjected) onVideoInjected(targetBay, selectedFile);
    } catch (err) {
      alert('Failed to inject video: ' + err.message);
    }
  };

  const handleProcessScan = async () => {
    if (!selectedFile) return;
    setProcessing(true);
    setScanSummary(null);
    setStatusMsg(`Scanning ${selectedFile} for damage-risk behaviors...`);
    try {
      const res = await processCustomVideoOffline(selectedFile, targetBay, activeCategory);
      setScanSummary(res.scan);
      setStatusMsg(res.message);
      if (onVideoInjected) onVideoInjected(targetBay, selectedFile);
    } catch (err) {
      alert('Offline video scan failed: ' + err.message);
    } finally {
      setProcessing(false);
    }
  };

  const handleResetFeed = async () => {
    try {
      await resetBayVideo(targetBay);
      setStatusMsg(`Reset ${targetBay} back to nominal camera feed.`);
      if (onVideoInjected) onVideoInjected(targetBay, null);
    } catch (err) {
      alert('Failed to reset: ' + err.message);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Film className="w-5 h-5 text-emerald-400" /> Custom Video Injection & Analysis Hub
          </h3>
          <p className="text-xs text-slate-400">
            Inject real warehouse MP4/AVI/MOV footage to run detection, tracking, risk scoring, and privacy shielding
          </p>
        </div>

        <button
          onClick={handleResetFeed}
          className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold flex items-center gap-1.5 transition-all self-start sm:self-auto"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Revert {targetBay} to Default
        </button>
      </div>

      {statusMsg && (
        <div className="p-3 rounded-xl bg-slate-950 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{statusMsg}</span>
        </div>
      )}

      {scanSummary && (
        <div className={`rounded-xl border p-4 space-y-2 ${
          scanSummary.detector_status === 'ready'
            ? 'border-cyan-500/30 bg-cyan-950/20'
            : 'border-amber-500/30 bg-amber-950/20'
        }`}>
          <p className="text-xs font-bold text-white">
            Video scan readings · {scanSummary.detector_status === 'ready' ? scanSummary.detector_model : 'Detector unavailable'}
          </p>
          <p className="text-[11px] text-slate-300">
            Frames analyzed: {scanSummary.frames_analyzed} of {scanSummary.frames_read}
            {' · '}Model detections: {Object.values(scanSummary.detection_counts).reduce((sum, count) => sum + count, 0)}
            {' · '}Risk events: {scanSummary.incident_count}
          </p>
          {Object.keys(scanSummary.detection_counts).length > 0 && (
            <p className="text-[11px] text-slate-300">
              Detected labels: {Object.entries(scanSummary.detection_counts).map(([label, count]) => `${label} (${count})`).join(', ')}
            </p>
          )}
          {scanSummary.detector_status !== 'ready' && (
            <p className="text-[11px] text-amber-200">
              {scanSummary.detector_error || 'Install Ultralytics and configure model weights to get actual detections.'}
              {' '}No detections does not mean the video is safe.
            </p>
          )}
          {scanSummary.detector_status === 'ready' && (
            <p className="text-[10px] text-slate-400">
              Warehouse labels supported: {scanSummary.warehouse_classes_supported.join(', ') || 'none'}.
              {' '}If carton or pallet labels are missing, the scan cannot assess those handling risks. Model outputs are not a damage-free loading certification.
            </p>
          )}
        </div>
      )}

      {/* Upload Zone & Config Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* Drag & Drop / File Picker Area */}
        <div
          onClick={() => fileInputRef.current?.click()}
          className="lg:col-span-5 border-2 border-dashed border-slate-700 hover:border-emerald-500 rounded-2xl p-6 flex flex-col items-center justify-center text-center cursor-pointer bg-slate-950/50 hover:bg-slate-950 transition-all group"
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="video/*"
            className="hidden"
            onChange={handleFileUpload}
          />
          <div className="p-3 rounded-2xl bg-emerald-500/10 text-emerald-400 group-hover:scale-110 transition-transform mb-3">
            <Upload className="w-6 h-6" />
          </div>
          <span className="text-xs font-bold text-white block">
            {uploading ? 'Uploading Video...' : 'Click or Drag to Upload Video File'}
          </span>
          <span className="text-[11px] text-slate-400 mt-1 block">
            Supports MP4, AVI, MOV, MKV, WebM (up to 500MB)
          </span>
        </div>

        {/* Target Bay & Video Selector */}
        <div className="lg:col-span-7 bg-slate-950/70 p-4 rounded-2xl border border-slate-800 space-y-3.5 text-xs">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-slate-400 font-semibold block mb-1">Target Loading Bay</label>
              <select
                value={targetBay}
                onChange={(e) => setTargetBay(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-white font-medium focus:outline-none focus:border-emerald-500"
              >
                {bays.map(b => (
                  <option key={b} value={b}>{b}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-slate-400 font-semibold block mb-1">Cargo Category</label>
              <select
                value={activeCategory}
                onChange={(e) => setActiveCategory(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-white font-medium focus:outline-none focus:border-emerald-500"
              >
                {categories.map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="text-slate-400 font-semibold block mb-1">Select Injected Video</label>
            {uploadedFiles.length === 0 ? (
              <p className="text-[11px] text-slate-400 py-1">No custom videos uploaded yet. Upload one on the left!</p>
            ) : (
              <select
                value={selectedFile || ''}
                onChange={(e) => setSelectedFile(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-white font-mono focus:outline-none focus:border-emerald-500"
              >
                {uploadedFiles.map(f => (
                  <option key={f.filename} value={f.filename}>
                    {f.filename} ({f.size_mb} MB)
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center gap-2.5 pt-1">
            <button
              disabled={!selectedFile || uploading}
              onClick={handleStreamVideo}
              className="flex-1 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold transition-all shadow-md shadow-emerald-600/20 flex items-center justify-center gap-1.5"
            >
              <Play className="w-3.5 h-3.5" /> Stream Live into {targetBay}
            </button>

            <button
              disabled={!selectedFile || processing}
              onClick={handleProcessScan}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-200 font-semibold transition-all border border-slate-700 flex items-center gap-1.5"
            >
              <Film className="w-3.5 h-3.5 text-cyan-400" />
              {processing ? 'Analyzing Video...' : 'Full Offline Scan'}
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
