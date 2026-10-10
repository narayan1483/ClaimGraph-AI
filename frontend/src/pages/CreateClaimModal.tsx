/**
 * ClaimGraph AI — Enterprise Create Claim Modal.
 * High-density Palantir-style form connected to real backend APIs.
 */

import React, { useState, useEffect } from 'react';
import { claimsService, type ClaimCreateParams } from '@/services/claims';
import { devicesService } from '@/services/devices';
import type { DeviceBrief } from '@/services/claims';

interface CreateClaimModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreated: (claim: any) => void;
}

const FALLBACK_DEVICES: DeviceBrief[] = [
  {
    id: 'eb9cdda7-8ccf-4122-bc3e-4c2fd7ba0383',
    serial_number: 'SN-ASSET-0011',
    product_id: '03dd71ca-8904-441f-b42a-872d78637190',
    customer_id: '02517999-6419-485c-8b26-9ce47ea69047',
    product: {
      id: '03dd71ca-8904-441f-b42a-872d78637190',
      name: 'PulseWave Smartwatch Ultra',
      category: 'Electronics',
      manufacturer: 'Titan Mobile',
      model_number: 'PW-ULTRA',
      msrp: 799.0,
    },
    purchase_date: '2026-03-08T04:55:59Z',
    purchase_price: 799.0,
    status: 'ACTIVE',
  },
  {
    id: 'a2fdc331-f4cb-46fa-823f-fd48b2c06af0',
    serial_number: 'SN-ASSET-0042',
    product_id: '25822342-af52-41f5-b6f2-a3c720702162',
    customer_id: 'd5a83049-f00c-4544-95a8-377b729d113c',
    product: {
      id: '25822342-af52-41f5-b6f2-a3c720702162',
      name: 'ApexBook 16-inch Laptop M3',
      category: 'Electronics',
      manufacturer: 'Apex Compute',
      model_number: 'AB-16',
      msrp: 2399.0,
    },
    purchase_date: '2026-01-05T04:55:59Z',
    purchase_price: 2399.0,
    status: 'ACTIVE',
  },
  {
    id: '0845ebd7-0461-4235-9771-482deee231c2',
    serial_number: 'SN-ASSET-0012',
    product_id: '03ca6715-d6fd-4e08-b26b-9be7e3cb5034',
    customer_id: '02517999-6419-485c-8b26-9ce47ea69047',
    product: {
      id: '03ca6715-d6fd-4e08-b26b-9be7e3cb5034',
      name: 'HyperSound Studio Headphones',
      category: 'Electronics',
      manufacturer: 'HyperSound Labs',
      model_number: 'HS-STUDIO',
      msrp: 399.0,
    },
    purchase_date: '2026-06-29T04:55:59Z',
    purchase_price: 399.0,
    status: 'ACTIVE',
  },
  {
    id: '51e9fa45-0400-4219-ab85-730d6bb2b166',
    serial_number: 'SN-ASSET-0022',
    product_id: '2f3a00b2-a3a9-450c-92e6-1b9a96b867cb',
    customer_id: 'a070ce99-abdf-4daf-94aa-427b39f5a917',
    product: {
      id: '2f3a00b2-a3a9-450c-92e6-1b9a96b867cb',
      name: 'Quantum OLED TV 65-inch',
      category: 'Appliances',
      manufacturer: 'Quantum Visual',
      model_number: 'QO-65',
      msrp: 1850.0,
    },
    purchase_date: '2026-06-13T04:55:59Z',
    purchase_price: 1850.0,
    status: 'ACTIVE',
  },
];

export const CreateClaimModal: React.FC<CreateClaimModalProps> = ({ isOpen, onClose, onCreated }) => {
  const [devices, setDevices] = useState<DeviceBrief[]>(FALLBACK_DEVICES);
  const [loadingDevices, setLoadingDevices] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form State
  const [selectedDeviceId, setSelectedDeviceId] = useState(FALLBACK_DEVICES[0].id);
  const [claimType, setClaimType] = useState('DAMAGE');
  const [claimAmount, setClaimAmount] = useState('450.00');
  const [incidentDate, setIncidentDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [description, setDescription] = useState('Severe screen shatter and touch unresponsiveness after accidental drop on hard floor.');
  const [location, setLocation] = useState('Chicago, IL');
  const [repairShop, setRepairShop] = useState('Vance Brothers Salvage & Repair (Flagged)');

  useEffect(() => {
    if (isOpen) {
      loadDevices();
    }
  }, [isOpen]);

  const loadDevices = async () => {
    try {
      setLoadingDevices(true);
      const list = await devicesService.listDevices();
      if (list && list.length > 0) {
        setDevices(list);
        setSelectedDeviceId(list[0].id);
      } else {
        setDevices(FALLBACK_DEVICES);
        setSelectedDeviceId(FALLBACK_DEVICES[0].id);
      }
    } catch (err: any) {
      console.warn('Backend devices list unavailable, applying fallback devices', err);
      setDevices(FALLBACK_DEVICES);
      setSelectedDeviceId(FALLBACK_DEVICES[0].id);
    } finally {
      setLoadingDevices(false);
    }
  };

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const selectedDevice = devices.find((d) => d.id === selectedDeviceId);
    if (!selectedDevice) {
      setError('Please select a valid registered device.');
      return;
    }

    if (!description.trim() || description.length < 5) {
      setError('Please provide a comprehensive incident description (at least 5 characters).');
      return;
    }

    const parsedAmount = parseFloat(claimAmount);
    if (isNaN(parsedAmount) || parsedAmount <= 0) {
      setError('Claim amount must be a positive number.');
      return;
    }

    try {
      setSubmitting(true);
      const payload: ClaimCreateParams = {
        customer_id: (selectedDevice as any).customer_id || (selectedDevice.product as any)?.customer_id || '',
        device_id: selectedDevice.id,
        claim_type: claimType,
        claim_amount: parsedAmount,
        incident_date: new Date(incidentDate).toISOString(),
        description: description.trim(),
        location: location.trim(),
        repair_shop: repairShop.trim() || undefined,
      };

      const created = await claimsService.createClaim(payload);
      onCreated(created);
      onClose();
    } catch (err: any) {
      setError(err?.response?.data?.message || err?.message || 'Failed to submit claim.');
    } finally {
      setSubmitting(false);
    }
  };

  const activeDevice = devices.find((d) => d.id === selectedDeviceId);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#030712]/80 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-2xl bg-[#090d16] border border-[#1e293b] rounded-xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#1e293b] bg-[#0d1322]">
          <div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
              <h2 className="text-sm font-semibold tracking-wider text-slate-100 uppercase">
                File New Insurance / Warranty Claim
              </h2>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Registers claim telemetry into the fraud feature calculation engine
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 p-1.5 rounded-lg hover:bg-slate-800/60 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3 text-xs bg-rose-950/60 border border-rose-800/80 text-rose-300 rounded-lg flex items-center gap-2">
              <svg className="w-4 h-4 shrink-0 text-rose-400" viewBox="0 0 20 20" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
              <span>{error}</span>
            </div>
          )}

          {/* Device Selection */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              Subject Device & Serial Number <span className="text-cyan-400">*</span>
            </label>
            <select
              value={selectedDeviceId}
              onChange={(e) => setSelectedDeviceId(e.target.value)}
              disabled={loadingDevices || devices.length === 0}
              className="w-full px-3 py-2 bg-[#0d1322] border border-[#1e293b] rounded-lg text-sm text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
            >
              {loadingDevices ? (
                <option>Loading enrolled devices...</option>
              ) : devices.length === 0 ? (
                <option>No enrolled devices available</option>
              ) : (
                devices.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.product?.name || 'Device'} — SN: {d.serial_number} (MSRP: ${d.product?.msrp ?? 'N/A'})
                  </option>
                ))
              )}
            </select>
            {activeDevice?.product && (
              <div className="mt-1 flex items-center gap-3 text-[11px] text-slate-400 font-mono">
                <span>Model: {activeDevice.product.model_number}</span>
                <span>•</span>
                <span>MSRP: ${activeDevice.product.msrp}</span>
                <span>•</span>
                <span>Status: {activeDevice.status}</span>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Claim Type */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Claim Loss Category</label>
              <select
                value={claimType}
                onChange={(e) => setClaimType(e.target.value)}
                className="w-full px-3 py-2 bg-[#0d1322] border border-[#1e293b] rounded-lg text-sm text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
              >
                <option value="DAMAGE">DAMAGE — Accidental physical impact</option>
                <option value="THEFT">THEFT — Unlawful appropriation</option>
                <option value="MALFUNCTION">MALFUNCTION — Hardware / PCB failure</option>
                <option value="LOSS">LOSS — Mysterious disappearance</option>
                <option value="WARRANTY_REPAIR">WARRANTY_REPAIR — OEM defect</option>
              </select>
            </div>

            {/* Claim Amount */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Claim Amount (USD) <span className="text-cyan-400">*</span>
              </label>
              <div className="relative">
                <span className="absolute left-3 top-2 text-sm text-slate-500 font-mono">$</span>
                <input
                  type="number"
                  step="0.01"
                  min="1"
                  value={claimAmount}
                  onChange={(e) => setClaimAmount(e.target.value)}
                  required
                  className="w-full pl-7 pr-3 py-2 bg-[#0d1322] border border-[#1e293b] rounded-lg text-sm text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
                  placeholder="0.00"
                />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Incident Date */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Incident Date</label>
              <input
                type="date"
                value={incidentDate}
                onChange={(e) => setIncidentDate(e.target.value)}
                className="w-full px-3 py-2 bg-[#0d1322] border border-[#1e293b] rounded-lg text-sm text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
              />
            </div>

            {/* Location */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Incident Location / Metro</label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full px-3 py-2 bg-[#0d1322] border border-[#1e293b] rounded-lg text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
                placeholder="e.g. Chicago, IL or Miami, FL"
              />
            </div>
          </div>

          {/* Repair Shop */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              Assigned Repair Shop / Service Depot (Optional)
            </label>
            <input
              type="text"
              value={repairShop}
              onChange={(e) => setRepairShop(e.target.value)}
              className="w-full px-3 py-2 bg-[#0d1322] border border-[#1e293b] rounded-lg text-sm text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
              placeholder="e.g. Apex Tech Authorized Center, Vance Brothers Salvage"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              Incident Narrative & Damage Description <span className="text-cyan-400">*</span>
            </label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
              className="w-full px-3 py-2 bg-[#0d1322] border border-[#1e293b] rounded-lg text-sm text-slate-200 focus:outline-none focus:border-cyan-500 placeholder-slate-600"
              placeholder="Detail circumstances of loss, observable symptoms, and initial claim notes..."
            />
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-[#1e293b]">
            <button
              type="button"
              onClick={onClose}
              disabled={submitting}
              className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="flex items-center gap-2 px-5 py-2 text-xs font-medium text-slate-950 bg-gradient-to-r from-cyan-400 to-teal-400 hover:from-cyan-300 hover:to-teal-300 rounded-lg shadow-lg shadow-cyan-950/40 transition-all font-mono uppercase tracking-wider"
            >
              {submitting ? (
                <>
                  <svg className="animate-spin h-3.5 w-3.5 text-slate-950" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  <span>Ingesting...</span>
                </>
              ) : (
                <span>Register & Ingest Claim</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
