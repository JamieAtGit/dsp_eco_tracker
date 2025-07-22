import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import ModernLayout, { ModernCard, ModernSection, ModernButton, ModernBadge, ModernInput } from "../components/ModernLayout";
import Header from "../components/Header";
import InsightsDashboard from "../components/InsightsDashboard";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line } from "recharts";

const BASE_URL = import.meta.env.VITE_API_BASE_URL;

const AdminStatCard = ({ title, value, subtitle, icon, color = "blue" }) => {
  const colorMap = {
    blue: "from-blue-500 to-cyan-500",
    purple: "from-purple-500 to-violet-500",
    green: "from-green-500 to-emerald-500",
    amber: "from-amber-500 to-orange-500",
    red: "from-red-500 to-rose-500"
  };

  return (
    <motion.div
      className="glass-card p-6"
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-slate-400 text-sm">{title}</p>
          <p className="text-2xl font-bold text-slate-200 mt-1">{value}</p>
          {subtitle && <p className="text-slate-500 text-xs mt-1">{subtitle}</p>}
        </div>
        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${colorMap[color]} flex items-center justify-center`}>
          <span className="text-white text-lg">{icon}</span>
        </div>
      </div>
    </motion.div>
  );
};

export default function AdminPage() {
  const [submissions, setSubmissions] = useState([]);
  const [selected, setSelected] = useState(null);
  const [updatedLabel, setUpdatedLabel] = useState("");
  const [metrics, setMetrics] = useState({});
  const [modelMetrics, setModelMetrics] = useState({});

  useEffect(() => {
    // Load submissions
    fetch(`${BASE_URL}/admin/submissions`, {
      method: "GET",
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => setSubmissions(data))
      .catch((err) => console.error("Error loading submissions:", err));

    // Load dashboard metrics for admin overview
    fetch(`${BASE_URL}/api/dashboard-metrics`)
      .then((res) => res.json())
      .then((data) => setMetrics(data))
      .catch((err) => console.error("Error loading metrics:", err));

    // Load model performance metrics
    fetch(`${BASE_URL}/model-metrics`)
      .then((res) => res.json())
      .then((data) => setModelMetrics(data))
      .catch((err) => console.error("Error loading model metrics:", err));
  }, []);

  const handleEdit = (index) => {
    setSelected(index);
    setUpdatedLabel(submissions[index].true_label || "");
  };

  const handleSave = () => {
    const item = { ...submissions[selected], true_label: updatedLabel };
    fetch(`${BASE_URL}/admin/update`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(item),
    })
      .then(() => {
        const updated = [...submissions];
        updated[selected].true_label = updatedLabel;
        setSubmissions(updated);
        setSelected(null);
      })
      .catch((err) => console.error("Update failed:", err));
  };

  // Calculate admin-specific metrics
  const submissionStats = {
    total: submissions.length,
    needsReview: submissions.filter(s => !s.true_label).length,
    accuracy: submissions.length > 0 ? 
      (submissions.filter(s => s.predicted_label === s.true_label).length / submissions.length * 100).toFixed(1) : 0,
    recentActivity: submissions.filter(s => {
      const submissionDate = new Date(s.timestamp || Date.now());
      const dayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
      return submissionDate > dayAgo;
    }).length
  };

  return (
    <ModernLayout>
      {{
        nav: <Header />,
        content: (
          <div className="space-y-8">
            {/* Hero Section */}
            <ModernSection className="text-center">
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, ease: "easeOut" }}
                className="space-y-6"
              >
                <h1 className="text-4xl md:text-5xl font-display font-bold leading-tight">
                  <span className="text-slate-100">Admin</span>
                  <br />
                  <span className="bg-gradient-to-r from-purple-400 via-pink-500 to-red-400 bg-clip-text text-transparent">
                    Dashboard
                  </span>
                </h1>
                <motion.p
                  className="text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.6, delay: 0.4 }}
                >
                  Monitor system performance, review predictions, and manage model accuracy.
                </motion.p>
              </motion.div>
            </ModernSection>

            {/* Admin Stats Grid */}
            <ModernSection>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <AdminStatCard
                  title="Total Submissions"
                  value={submissionStats.total}
                  subtitle="All predictions"
                  icon="📊"
                  color="blue"
                />
                <AdminStatCard
                  title="Needs Review"
                  value={submissionStats.needsReview}
                  subtitle="Missing labels"
                  icon="⚠️"
                  color="amber"
                />
                <AdminStatCard
                  title="Model Accuracy"
                  value={`${submissionStats.accuracy}%`}
                  subtitle="Prediction success"
                  icon="🎯"
                  color="green"
                />
                <AdminStatCard
                  title="Recent Activity"
                  value={submissionStats.recentActivity}
                  subtitle="Last 24 hours"
                  icon="⚡"
                  color="purple"
                />
              </div>
            </ModernSection>

            {/* System Overview */}
            <ModernSection 
              title="System Analytics" 
              icon={true}
              delay={0.2}
            >
              <InsightsDashboard />
            </ModernSection>

            {/* Prediction Management */}
            <ModernSection 
              title="Prediction Review" 
              icon={true}
              delay={0.4}
            >
              <ModernCard solid>
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-display text-slate-200">
                      Review & Validate Predictions
                    </h3>
                    <ModernBadge variant="info" size="sm">
                      {submissions.length} items
                    </ModernBadge>
                  </div>

                  {/* Enhanced Table */}
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-slate-600">
                          <th className="text-left p-3 text-slate-300 font-medium">Product Title</th>
                          <th className="text-left p-3 text-slate-300 font-medium">Predicted</th>
                          <th className="text-left p-3 text-slate-300 font-medium">Confidence</th>
                          <th className="text-left p-3 text-slate-300 font-medium">True Label</th>
                          <th className="text-left p-3 text-slate-300 font-medium">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Array.isArray(submissions) && submissions.length > 0 ? (
                          submissions.map((item, index) => (
                            <motion.tr 
                              key={index} 
                              className="border-b border-slate-700/50 hover:bg-slate-800/30"
                              initial={{ opacity: 0, y: 10 }}
                              animate={{ opacity: 1, y: 0 }}
                              transition={{ duration: 0.3, delay: index * 0.05 }}
                            >
                              <td className="p-3 text-slate-300">
                                <div className="max-w-xs truncate">{item.title}</div>
                              </td>
                              <td className="p-3">
                                <ModernBadge 
                                  variant={
                                    item.predicted_label === 'A+' || item.predicted_label === 'A' ? 'success' : 
                                    item.predicted_label === 'B' || item.predicted_label === 'C' ? 'warning' : 'error'
                                  }
                                  size="sm"
                                >
                                  {item.predicted_label}
                                </ModernBadge>
                              </td>
                              <td className="p-3 text-slate-400">
                                {item.confidence || "N/A"}
                              </td>
                              <td className="p-3">
                                {index === selected ? (
                                  <ModernInput
                                    type="text"
                                    value={updatedLabel}
                                    onChange={(e) => setUpdatedLabel(e.target.value)}
                                    placeholder="A+, A, B, C, D, E, F"
                                    className="w-24"
                                  />
                                ) : (
                                  <span className="text-slate-300">
                                    {item.true_label || <span className="text-slate-500">—</span>}
                                  </span>
                                )}
                              </td>
                              <td className="p-3">
                                {index === selected ? (
                                  <div className="flex gap-2">
                                    <ModernButton
                                      variant="success"
                                      size="sm"
                                      onClick={handleSave}
                                    >
                                      Save
                                    </ModernButton>
                                    <ModernButton
                                      variant="secondary"
                                      size="sm"
                                      onClick={() => setSelected(null)}
                                    >
                                      Cancel
                                    </ModernButton>
                                  </div>
                                ) : (
                                  <ModernButton
                                    variant="secondary"
                                    size="sm"
                                    onClick={() => handleEdit(index)}
                                  >
                                    Edit
                                  </ModernButton>
                                )}
                              </td>
                            </motion.tr>
                          ))
                        ) : (
                          <tr>
                            <td colSpan="5" className="text-center p-8 text-slate-400">
                              <div className="space-y-2">
                                <div className="text-3xl">📭</div>
                                <p>No submissions found or access denied.</p>
                                <p className="text-sm text-slate-500">Make some predictions to see data here.</p>
                              </div>
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </ModernCard>
            </ModernSection>

            {/* Footer */}
            <motion.footer
              className="text-center py-12 mt-16"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.8 }}
            >
              <ModernCard className="max-w-md mx-auto text-center">
                <div className="space-y-2">
                  <p className="text-slate-300 font-medium">
                    © 2025 Impact Tracker Admin
                  </p>
                  <p className="text-slate-400 text-sm">
                    Monitoring system performance 🔧
                  </p>
                </div>
              </ModernCard>
            </motion.footer>
          </div>
        ),
      }}
    </ModernLayout>
  );
}
