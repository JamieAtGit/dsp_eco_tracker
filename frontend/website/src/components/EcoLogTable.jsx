import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ModernCard, ModernButton, ModernInput, ModernBadge } from "./ModernLayout";

const BASE_URL = import.meta.env.VITE_API_BASE_URL;

export default function EcoLogTable() {
  const [data, setData] = useState([]);
  const [scoreFilter, setScoreFilter] = useState("");
  const [materialFilter, setMaterialFilter] = useState("");
  const [isExpanded, setIsExpanded] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    fetch(`${BASE_URL}/api/eco-data`)
      .then((res) => res.json())
      .then((rows) => setData(rows))
      .catch((err) => console.error("Error loading eco data:", err));
  }, []);

  if (!Array.isArray(data)) {
    console.error("❌ Expected array but got:", data);
    return <p>Failed to load data.</p>;
  }
  
  const filteredData = data.filter((row) => {
    const matchesScore = scoreFilter === "" || row.eco_score === scoreFilter;
    const matchesMaterial = materialFilter === "" || row.material === materialFilter;
    const matchesSearch = searchTerm === "" || 
      row.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      row.material?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      row.origin?.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesScore && matchesMaterial && matchesSearch;
  });

  const uniqueScores = [...new Set(data.map((row) => row.eco_score))];
  const uniqueMaterials = [...new Set(data.map((row) => row.material))];

  const downloadCSV = () => {
    const headers = [
      "title",
      "material",
      "weight",
      "transport",
      "recyclability",
      "eco_score",
      "co2_emissions",
      "origin",
    ];
    const csvRows = [headers.join(",")];
    filteredData.forEach((row) => {
      const values = headers.map((h) => JSON.stringify(row[h] || ""));
      csvRows.push(values.join(","));
    });
    const csvData = new Blob([csvRows.join("\n")], { type: "text/csv" });
    const url = URL.createObjectURL(csvData);
    const link = document.createElement("a");
    link.href = url;
    link.download = "eco_dataset.csv";
    link.click();
  };

  return (
    <ModernCard className="max-w-7xl mx-auto" solid>
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:justify-between lg:items-center gap-4 mb-6">
        <div className="flex items-center gap-3">
          <div className="status-indicator status-success"></div>
          <h2 className="text-xl font-display text-slate-200">
            Product Impact Database
          </h2>
        </div>
        <ModernButton
          variant="secondary"
          size="sm"
          onClick={downloadCSV}
          icon="💾"
        >
          Download CSV
        </ModernButton>
      </div>

      {/* Filters */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <ModernInput
          label="Search Products"
          type="text"
          placeholder="Search products..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          icon="🔍"
        />
        
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Eco Score
          </label>
          <select
            className="input-modern text-sm"
            value={scoreFilter}
            onChange={(e) => setScoreFilter(e.target.value)}
          >
            <option value="">All Scores</option>
            {uniqueScores.map((score, index) => (
              <option key={index} value={score}>{score}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Material Type
          </label>
          <select
            className="input-modern text-sm"
            value={materialFilter}
            onChange={(e) => setMaterialFilter(e.target.value)}
          >
            <option value="">All Materials</option>
            {uniqueMaterials.map((mat) => (
              <option key={mat} value={mat}>{mat}</option>
            ))}
          </select>
        </div>

        <div className="flex items-end">
          <ModernButton
            variant={isExpanded ? "primary" : "secondary"}
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
            icon={isExpanded ? "📋" : "📦"}
            className="w-full"
          >
            {isExpanded ? 'Hide Data' : 'Show Data'}
          </ModernButton>
        </div>
      </motion.div>

      {/* Results Count */}
      <motion.div
        className="flex items-center justify-between mb-4 p-3 glass-card rounded-lg"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <div className="flex items-center gap-2">
          <ModernBadge variant="info" size="sm">
            {filteredData.length} found
          </ModernBadge>
          <span className="text-sm text-slate-400">
            of {data.length} total products
          </span>
        </div>
      </motion.div>

      {/* Product Grid */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.4, ease: "easeInOut" }}
          >
            {filteredData.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 max-h-96 overflow-y-auto">
                {filteredData.map((row, i) => (
                  <motion.div
                    key={i}
                    className="glass-card p-4 card-hover"
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.3, delay: i * 0.02 }}
                  >
                    <div className="space-y-3">
                      <h4 className="font-medium text-slate-200 text-sm leading-tight line-clamp-2">
                        {row.title}
                      </h4>
                      
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div className="flex justify-between">
                          <span className="text-slate-400">Material:</span>
                          <ModernBadge variant="default" size="sm">
                            {row.material}
                          </ModernBadge>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Weight:</span>
                          <span className="text-slate-300 font-medium">{row.weight} kg</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Transport:</span>
                          <span className="text-slate-300 font-medium">{row.transport}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Score:</span>
                          <ModernBadge 
                            variant={row.eco_score === 'A+' || row.eco_score === 'A' ? 'success' : 
                                   row.eco_score === 'B' || row.eco_score === 'C' ? 'warning' : 'error'} 
                            size="sm"
                          >
                            {row.eco_score}
                          </ModernBadge>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">CO₂:</span>
                          <span className="text-red-400 font-medium">{row.co2_emissions} kg</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Origin:</span>
                          <span className="text-slate-300 font-medium">{row.origin}</span>
                        </div>
                      </div>
                      
                      <div className="pt-2 border-t border-slate-600">
                        <div className="flex justify-between items-center">
                          <span className="text-slate-400 text-xs">Recyclability:</span>
                          <ModernBadge 
                            variant={row.recyclability === 'High' ? 'success' : 
                                   row.recyclability === 'Medium' ? 'warning' : 'error'} 
                            size="sm"
                          >
                            {row.recyclability}
                          </ModernBadge>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            ) : (
              <motion.div
                className="text-center py-12 glass-card"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.5 }}
              >
                <div className="text-4xl mb-4">🔍</div>
                <p className="text-slate-300 font-medium mb-2">No products match your filters</p>
                <p className="text-slate-400 text-sm">Try adjusting your search criteria</p>
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

    </ModernCard>
  );
}
