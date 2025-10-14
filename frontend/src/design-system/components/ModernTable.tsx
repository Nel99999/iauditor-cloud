import React from 'react';
import GlassCard from './GlassCard';
import { motion } from 'framer-motion';
import './ModernTable.css';

interface TableColumn<T = any> {
  header: string;
  accessor?: string;
  render?: (row: T) => React.ReactNode;
}

interface ModernTableProps<T = any> {
  columns: TableColumn<T>[];
  data: T[];
  loading?: boolean;
  onRowClick?: (row: T) => void;
}

const ModernTable = <T extends Record<string, any>>({
  columns,
  data,
  loading = false,
  onRowClick
}: ModernTableProps<T>) => {
  if (loading) {
    return (
      <GlassCard padding="lg" className="modern-table-loading">
        <div className="loading-spinner">Loading...</div>
      </GlassCard>
    );
  }

  if (!data || data.length === 0) {
    return (
      <GlassCard padding="lg" className="modern-table-empty">
        <p className="empty-message">No data available</p>
      </GlassCard>
    );
  }

  return (
    <GlassCard padding="none" className="modern-table-container">
      <div className="table-wrapper">
        <table className="modern-table">
          <thead>
            <tr>
              {columns.map((column, index) => (
                <th key={index} className="table-header">
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, rowIndex) => (
              <motion.tr
                key={rowIndex}
                className="table-row"
                onClick={() => onRowClick && onRowClick(row)}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: rowIndex * 0.05, duration: 0.3 }}
                whileHover={{ backgroundColor: 'var(--color-neutral-100)' }}
              >
                {columns.map((column, colIndex) => (
                  <td key={colIndex} className="table-cell">
                    {column.render ? column.render(row) : row[column.accessor as string]}
                  </td>
                ))}
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </GlassCard>
  );
};

export default ModernTable;
