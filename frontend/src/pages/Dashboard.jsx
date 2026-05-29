import AIOperationsConsole from "../components/dashboard/AIOperationsConsole.jsx";
import EventOverview from "../components/dashboard/EventOverview.jsx";
import IncidentsTable from "../components/dashboard/IncidentsTable.jsx";
import OperationPlan from "../components/dashboard/OperationPlan.jsx";
import RiskAssessment from "../components/dashboard/RiskAssessment.jsx";
import TopBar from "../components/layout/TopBar.jsx";
import {
  mockConsoleHistory,
  mockEvent,
  mockIncidents,
  mockOperationPlan,
  mockRisk,
} from "../data/mockDashboard.js";

export default function Dashboard() {
  return (
    <div className="min-h-screen pb-8">
      <TopBar event={mockEvent} />

      <main className="mx-auto max-w-[1600px] space-y-6 px-4 py-6 sm:px-6 lg:px-8">
        <EventOverview event={mockEvent} />

        <div className="grid gap-6 xl:grid-cols-12">
          <div className="space-y-6 xl:col-span-8">
            <div className="grid gap-6 lg:grid-cols-2">
              <RiskAssessment risk={mockRisk} />
              <OperationPlan plan={mockOperationPlan} />
            </div>
            <IncidentsTable incidents={mockIncidents} />
          </div>

          <div className="xl:col-span-4">
            <div className="sticky top-28 xl:max-h-[calc(100vh-8rem)]">
              <AIOperationsConsole initialMessages={mockConsoleHistory} />
            </div>
          </div>
        </div>
      </main>

      <footer className="mx-auto max-w-[1600px] px-4 pb-4 text-center text-xs text-slate-600 sm:px-6 lg:px-8">
        CrowdPilot AI · Event Operations Platform · Hackathon MVP
      </footer>
    </div>
  );
}
