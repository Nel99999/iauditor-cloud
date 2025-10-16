import React, { useState } from 'react';
import axios from 'axios';
import { Upload, Download, FileText, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

const BulkImportPage: React.FC = () => {
  const [file, setFile] = useState<any | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [validationResults, setValidationResults] = useState<any | null>(null);
  const [importResults, setImportResults] = useState<any | null>(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'text/csv') {
      setFile(selectedFile);
      setValidationResults(null);
      setImportResults(null);
    } else {
      alert('Please select a valid CSV file');
    }
  };

  const handleValidate = async () => {
    if (!file) {
      alert('Please select a file first');
      return;
    }

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append('file', file);

      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'
      };

      const response = await axios.post(
        `${API_BASE_URL}/api/bulk-import/validate`,
        formData,
        { headers }
      );

      setValidationResults(response.data);
    } catch (err: unknown) {
      console.error('Error validating file:', err);
      alert((err as any).response?.data?.detail || 'Failed to validate file');
    } finally {
      setUploading(false);
    }
  };

  const handleImport = async () => {
    if (!file || !validationResults || !validationResults.is_valid) {
      alert('Please validate the file first');
      return;
    }

    if (!window.confirm(`Import ${validationResults.valid_count} users?`)) {
      return;
    }

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append('file', file);

      const token = localStorage.getItem('token') || localStorage.getItem('access_token');
      const headers = {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'
      };

      const response = await axios.post(
        `${API_BASE_URL}/api/bulk-import/users`,
        formData,
        { headers }
      );

      setImportResults(response.data);
      setFile(null);
      setValidationResults(null);
    } catch (err: unknown) {
      console.error('Error importing users:', err);
      alert((err as any).response?.data?.detail || 'Failed to import users');
    } finally {
      setUploading(false);
    }
  };

  const downloadTemplate: React.FC = () => {
    const csvContent = 'email,name,role\nexample@company.com,John Doe,viewer\ntest@company.com,Jane Smith,editor';
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'user_import_template.csv';
    a.click();
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
            <Upload className="w-8 h-8 text-blue-600" />
            Bulk User Import
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Import multiple users at once using a CSV file
          </p>
        </div>

        {/* Instructions Card */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            How to Import Users
          </h2>
          <ol className="list-decimal list-inside space-y-2 text-gray-600 dark:text-gray-400">
            <li>Download the CSV template below</li>
            <li>Fill in the user details (email, name, role)</li>
            <li>Upload the completed CSV file</li>
            <li>Review validation results</li>
            <li>Confirm import to add users</li>
          </ol>

          <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <p className="text-sm text-blue-800 dark:text-blue-300">
              <strong>Required columns:</strong> email, name, role
              <br />
              <strong>Valid roles:</strong> viewer, editor, supervisor, manager, developer, master
            </p>
          </div>

          <button
            onClick={downloadTemplate}
            className="mt-4 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            Download CSV Template
          </button>
        </div>

        {/* Upload Section */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Upload CSV File
          </h2>

          <div className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg p-8 text-center">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="hidden"
              id="csv-upload"
            />
            <label
              htmlFor="csv-upload"
              className="cursor-pointer text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
            >
              Click to upload CSV file
            </label>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
              or drag and drop
            </p>
          </div>

          {file && (
            <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg flex items-center justify-between">
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-blue-600" />
                <span className="text-gray-900 dark:text-white">{file.name}</span>
              </div>
              <button
                onClick={() => {
                  setFile(null);
                  setValidationResults(null);
                  setImportResults(null);
                }}
                className="text-red-600 hover:text-red-700 text-sm"
              >
                Remove
              </button>
            </div>
          )}

          {file && !validationResults && (
            <button
              onClick={handleValidate}
              disabled={uploading}
              className="mt-4 w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploading ? 'Validating...' : 'Validate File'}
            </button>
          )}
        </div>

        {/* Validation Results */}
        {validationResults && (
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Validation Results
            </h2>

            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400 mb-2">
                  <FileText className="w-5 h-5" />
                  <span className="text-sm font-medium">Total Rows</span>
                </div>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {validationResults.total_count}
                </p>
              </div>

              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <div className="flex items-center gap-2 text-green-600 dark:text-green-400 mb-2">
                  <CheckCircle className="w-5 h-5" />
                  <span className="text-sm font-medium">Valid</span>
                </div>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {validationResults.valid_count}
                </p>
              </div>

              <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                <div className="flex items-center gap-2 text-red-600 dark:text-red-400 mb-2">
                  <XCircle className="w-5 h-5" />
                  <span className="text-sm font-medium">Invalid</span>
                </div>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {validationResults.invalid_count}
                </p>
              </div>
            </div>

            {/* Validation Errors */}
            {validationResults.errors && validationResults.errors.length > 0 && (
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-red-600" />
                  Validation Errors
                </h3>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {validationResults.errors.map((error, index) => (
                    <div
                      key={index}
                      className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm"
                    >
                      <p className="text-red-800 dark:text-red-300">
                        <strong>Row {error.row}:</strong> {error.message}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Preview Valid Data */}
            {validationResults.preview && validationResults.preview.length > 0 && (
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
                  Preview (first 5 valid rows)
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-200 dark:border-gray-700">
                        <th className="text-left py-2 px-3 text-sm font-medium text-gray-600 dark:text-gray-400">
                          Email
                        </th>
                        <th className="text-left py-2 px-3 text-sm font-medium text-gray-600 dark:text-gray-400">
                          Name
                        </th>
                        <th className="text-left py-2 px-3 text-sm font-medium text-gray-600 dark:text-gray-400">
                          Role
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {validationResults.preview.map((row, index) => (
                        <tr
                          key={index}
                          className="border-b border-gray-200 dark:border-gray-700"
                        >
                          <td className="py-2 px-3 text-sm text-gray-900 dark:text-white">
                            {row.email}
                          </td>
                          <td className="py-2 px-3 text-sm text-gray-900 dark:text-white">
                            {row.name}
                          </td>
                          <td className="py-2 px-3 text-sm text-gray-900 dark:text-white">
                            <span className="px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 rounded-full text-xs">
                              {row.role}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Import Button */}
            {validationResults.is_valid && validationResults.valid_count > 0 && (
              <button
                onClick={handleImport}
                disabled={uploading}
                className="w-full px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
              >
                {uploading ? 'Importing...' : `Import ${validationResults.valid_count} Users`}
              </button>
            )}

            {!validationResults.is_valid && (
              <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <p className="text-red-800 dark:text-red-300 text-sm">
                  Please fix all validation errors before importing
                </p>
              </div>
            )}
          </div>
        )}

        {/* Import Results */}
        {importResults && (
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Import Complete
            </h2>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <div className="flex items-center gap-2 text-green-600 dark:text-green-400 mb-2">
                  <CheckCircle className="w-5 h-5" />
                  <span className="text-sm font-medium">Successfully Imported</span>
                </div>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {importResults.success_count}
                </p>
              </div>

              <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                <div className="flex items-center gap-2 text-red-600 dark:text-red-400 mb-2">
                  <XCircle className="w-5 h-5" />
                  <span className="text-sm font-medium">Failed</span>
                </div>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {importResults.failed_count}
                </p>
              </div>
            </div>

            {importResults.failed_users && importResults.failed_users.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-red-600" />
                  Failed Imports
                </h3>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {importResults.failed_users.map((failure, index) => (
                    <div
                      key={index}
                      className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm"
                    >
                      <p className="text-red-800 dark:text-red-300">
                        <strong>{failure.email}:</strong> {failure.reason}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <button
              onClick={() => {
                setImportResults(null);
                setFile(null);
              }}
              className="mt-6 w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Import More Users
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default BulkImportPage;
