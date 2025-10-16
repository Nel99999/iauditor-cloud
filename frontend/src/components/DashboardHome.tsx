import DashboardHomeNew from './DashboardHomeNew';

// Legacy DashboardHome component - re-exports DashboardHomeNew for backwards compatibility
const DashboardHome = () => {
  return <DashboardHomeNew />;
};

export default DashboardHome;
