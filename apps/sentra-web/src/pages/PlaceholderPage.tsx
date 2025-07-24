import React from 'react';

interface PlaceholderPageProps {
  title: string;
}

const PlaceholderPage: React.FC<PlaceholderPageProps> = ({ title }) => {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-slate-800 mb-4">{title}</h1>
        <p className="text-lg text-slate-600 mb-8">Coming soon...</p>
        <div className="text-sm text-slate-400">
          This feature is under development and will be available in a future release.
        </div>
      </div>
    </div>
  );
};

export default PlaceholderPage;