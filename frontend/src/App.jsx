// App.jsx — Root component with tab routing and modal management
import React, { useState } from 'react';
import { Navbar } from './components/ui/Navbar';
import { AboutPage } from './components/about/AboutPage';
import { Overview } from './components/dashboard/Overview';
import { ReturnsQueue } from './components/returns/ReturnsQueue';
import { Simulator } from './components/simulator/Simulator';
import { ModelMetrics } from './components/models/ModelMetrics';
import { AuditVault } from './components/audit/AuditVault';
import { InspectorModal } from './components/ui/InspectorModal';
import { ToastProvider } from './components/ui/Toast';

export default function App() {
  const [tab, setTab] = useState('overview');
  const [modal, setModal] = useState(null); // { returnId, customerId }

  function openInspect(returnId, customerId) {
    setModal({ returnId, customerId });
  }

  return (
    <ToastProvider>
      <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Navbar activeTab={tab} onTabChange={setTab} />

        <main className="main-content">
          {tab === 'about'      && <AboutPage onNavigate={setTab} />}
          {tab === 'overview'   && <Overview onInspect={openInspect} />}
          {tab === 'returns'    && <ReturnsQueue onInspect={openInspect} />}
          {tab === 'simulator'  && <Simulator />}
          {tab === 'models'     && <ModelMetrics />}
          {tab === 'audit'      && <AuditVault />}
        </main>

        {modal && (
          <InspectorModal
            returnId={modal.returnId}
            customerId={modal.customerId}
            onClose={() => setModal(null)}
          />
        )}
      </div>
    </ToastProvider>
  );
}
