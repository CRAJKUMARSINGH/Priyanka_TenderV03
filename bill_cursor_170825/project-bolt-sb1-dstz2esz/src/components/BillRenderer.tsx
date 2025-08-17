import React, { useState, useRef } from 'react';
import { FileText, Download, Eye, Upload, FileSpreadsheet } from 'lucide-react';
import { BillData } from '../types/BillData';
import { readExcelFile } from '../utils/fileHandlers';
import { TemplateRenderer } from '../utils/templateRenderer';

const BillRenderer: React.FC = () => {
  const [billData, setBillData] = useState<BillData | null>(null);
  const [activeTemplate, setActiveTemplate] = useState<string>('first_page');
  const [renderedContent, setRenderedContent] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileUpload = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const data = await readExcelFile();
      if (data) {
        setBillData(data);
        renderTemplate(activeTemplate, data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process the file');
      console.error('Error processing file:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const renderTemplate = (templateName: string, data: BillData) => {
    let content = '';
    
    switch (templateName) {
      case 'first_page':
        content = TemplateRenderer.renderFirstPage(data);
        break;
      case 'certificate_ii':
        content = TemplateRenderer.renderCertificateII(data);
        break;
      case 'certificate_iii':
        content = TemplateRenderer.renderCertificateIII(data);
        break;
      case 'deviation_statement':
        content = TemplateRenderer.renderDeviationStatement(data);
        break;
      case 'extra_items':
        content = TemplateRenderer.renderExtraItems(data);
        break;
      default:
        content = '<p>Template not found</p>';
    }
    
    setRenderedContent(content);
    setActiveTemplate(templateName);
  };

  const handleDownloadPDF = () => {
    if (!renderedContent) return;
    
    const printWindow = window.open('', '_blank');
    if (printWindow) {
      printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <title>Contractor Bill</title>
          <style>
            @page { size: A4; margin: 10mm; }
            body { font-family: Arial, sans-serif; font-size: 10pt; margin: 0; padding: 20px; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
            th, td { border: 1px solid black; padding: 4px; text-align: left; vertical-align: top; }
            th { font-weight: bold; text-align: center; background-color: #f0f0f0; }
            .text-right { text-align: right; }
            .text-center { text-align: center; }
            h1, h2 { text-align: center; margin-bottom: 20px; }
            .bill-page, .certificate-page, .deviation-page, .extra-items-page { page-break-after: always; }
            .bill-page:last-child, .certificate-page:last-child, .deviation-page:last-child, .extra-items-page:last-child { page-break-after: auto; }
          </style>
        </head>
        <body>
          ${renderedContent}
        </body>
        </html>
      `);
      printWindow.document.close();
      printWindow.print();
    }
  };

  const handlePreview = () => {
    // Your existing preview logic
  };

  // If no bill data is loaded, show the upload screen
  if (!billData) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-6">
        <div className="w-full max-w-md bg-white rounded-lg shadow-md p-8">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-gray-800 mb-2">Bill Generator</h1>
            <p className="text-gray-600">Upload your Excel file to generate bills</p>
          </div>
          
          <div 
            className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:bg-gray-50 transition-colors"
            onClick={handleFileUpload}
          >
            <div className="flex flex-col items-center justify-center space-y-4">
              <div className="p-3 bg-blue-50 rounded-full">
                <Upload className="w-8 h-8 text-blue-500" />
              </div>
              <div>
                <p className="font-medium text-gray-700">Click to upload or drag and drop</p>
                <p className="text-sm text-gray-500 mt-1">Excel files only (.xlsx, .xls)</p>
              </div>
              <button
                type="button"
                className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
                disabled={isLoading}
                onClick={(e) => {
                  e.stopPropagation();
                  handleFileUpload();
                }}
              >
                {isLoading ? 'Processing...' : 'Select File'}
              </button>
            </div>
          </div>
          
          {error && (
            <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-md text-sm">
              {error}
            </div>
          )}
          
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-500">
              Need a sample file? <a href="#" className="text-blue-600 hover:underline">Download template</a>
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Your existing bill rendering UI
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {/* Header */}
          <div className="bg-gray-800 text-white p-4 flex justify-between items-center">
            <h1 className="text-xl font-bold">Bill Generator</h1>
            <div className="flex space-x-2">
              <button
                onClick={handleFileUpload}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
              >
                <FileSpreadsheet className="w-4 h-4" />
                Upload New File
              </button>
              <button
                onClick={handlePreview}
                className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
              >
                <Eye className="w-4 h-4" />
                Preview
              </button>
              <button
                onClick={handleDownloadPDF}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Download PDF
              </button>
            </div>
          </div>

          {/* Template Selection */}
          <div className="bg-gray-100 p-2 flex space-x-2 overflow-x-auto">
            {[
              { id: 'first_page', name: 'First Page', icon: FileText },
              { id: 'deviation_statement', name: 'Deviation', icon: FileText },
              { id: 'extra_items', name: 'Extra Items', icon: FileText },
              { id: 'note_sheet', name: 'Note Sheet', icon: FileText },
              { id: 'certificate_ii', name: 'Certificate II', icon: FileText },
              { id: 'certificate_iii', name: 'Certificate III', icon: FileText },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => renderTemplate(tab.id, billData)}
                className={`px-4 py-2 rounded-md flex items-center gap-2 whitespace-nowrap ${
                  activeTemplate === tab.id
                    ? 'bg-blue-100 text-blue-700'
                    : 'hover:bg-gray-200'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.name}
              </button>
            ))}
          </div>

          {/* Rendered Content */}
          <div className="p-6">
            {renderedContent ? (
              <div dangerouslySetInnerHTML={{ __html: renderedContent }} />
            ) : (
              <div className="text-center py-12 text-gray-500">
                Select a template to render
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BillRenderer;