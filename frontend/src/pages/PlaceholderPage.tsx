/**
 * ClaimGraph AI — Placeholder Page.
 *
 * Clean "coming soon" page for routes that will be implemented in future phases.
 * Does NOT create fake UI — just states what will come and when.
 */

import { Construction } from 'lucide-react';

interface PlaceholderPageProps {
  title: string;
  description: string;
  phase: string;
  features: string[];
}

export default function PlaceholderPage({ title, description, phase, features }: PlaceholderPageProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] animate-fade-in">
      <div className="glass rounded-2xl p-10 max-w-lg w-full text-center">
        <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-600/15">
          <Construction size={32} className="text-brand-400" />
        </div>
        <h1 className="text-2xl font-bold text-white">{title}</h1>
        <p className="mt-2 text-sm text-surface-600">{description}</p>
        <div className="mt-2 inline-block rounded-full bg-surface-800 px-3 py-1 text-xs font-semibold text-brand-400">
          {phase}
        </div>

        <div className="mt-6 text-left">
          <p className="text-xs font-semibold uppercase tracking-wider text-surface-600 mb-3">
            Planned Features
          </p>
          <ul className="space-y-2">
            {features.map((feature) => (
              <li key={feature} className="flex items-center gap-2 text-sm text-surface-600">
                <span className="h-1.5 w-1.5 rounded-full bg-brand-500 shrink-0" />
                {feature}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
