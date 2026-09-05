// App.jsx — Root component with sidebar routing and modal management
import React, { useState } from 'react';
import { Sidebar, MobileHeader } from './components/ui/Sidebar';
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
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  function openInspect(returnId, customerId) {
    setModal({ returnId, customerId });
  }

  return (
    <ToastProvider>
      <div className="app-layout">
        {/* Mobile Header (shown on screens < 1024px) */}
        <MobileHeader 
          activeTab={tab} 
          onToggleMobile={() => setMobileOpen(!mobileOpen)} 
        />

        {/* Sidebar Navigation (Behance style) */}
        <Sidebar
          activeTab={tab}
          onTabChange={setTab}
          isCollapsed={isCollapsed}
          onToggleCollapse={() => setIsCollapsed(!isCollapsed)}
          mobileOpen={mobileOpen}
          onMobileClose={() => setMobileOpen(false)}
        />

        {/* Main Content Area */}
        <div className="main-viewport">
          <main className="main-content">
            {tab === 'about'      && <AboutPage onNavigate={setTab} />}
            {tab === 'overview'   && <Overview onInspect={openInspect} />}
            {tab === 'returns'    && <ReturnsQueue onInspect={openInspect} />}
            {tab === 'simulator'  && <Simulator />}
            {tab === 'models'     && <ModelMetrics />}
            {tab === 'audit'      && <AuditVault />}
          </main>
        </div>

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
