import { invoke } from '@tauri-apps/api/tauri';
import * as XLSX from 'xlsx';
import { BillData } from '../types/BillData';

export async function readExcelFile(): Promise<BillData | null> {
  try {
    // Open file dialog to select Excel file
    const selected = await invoke('dialog:open', {
      multiple: false,
      filters: [{
        name: 'Excel',
        extensions: ['xlsx', 'xls']
      }]
    });

    if (!selected) return null;

    // Read the file as binary
    const contents = await invoke('fs:read', {
      path: selected.path,
      binary: true
    });
    
    // Parse Excel file
    const workbook = XLSX.read(contents, { type: 'array' });
    
    // Process the first sheet
    const firstSheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[firstSheetName];
    
    // Convert to JSON
    const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
    
    // Map the Excel data to BillData format
    return mapExcelToBillData(jsonData);
    
  } catch (error) {
    console.error('Error reading Excel file:', error);
    throw new Error('Failed to read the Excel file. Please try again.');
  }
}

// Helper function to map Excel data to BillData format
function mapExcelToBillData(excelData: any[][]): BillData {
  // TODO: Implement the actual mapping based on your Excel structure
  // This is a placeholder implementation
  return {
    agreement_no: "",
    name_of_work: "",
    name_of_firm: "",
    date_commencement: "",
    date_completion: "",
    actual_completion: "",
    bill_items: [],
    extra_items: [],
    deviation_items: [],
    bill_total: 0,
    bill_premium: 0,
    bill_grand_total: 0,
    extra_items_base: 0,
    extra_premium: 0,
    extra_items_sum: 0,
    tender_premium_percent: 0.05,
    deviation_summary: {
      work_order_total: 0,
      tender_premium_f: 0,
      grand_total_f: 0,
      executed_total: 0,
      tender_premium_h: 0,
      grand_total_h: 0,
      overall_excess: 0,
      tender_premium_j: 0,
      grand_total_j: 0,
      overall_saving: 0,
      tender_premium_l: 0,
      grand_total_l: 0,
      net_difference: 0
    },
    totals: {
      grand_total: 0,
      sd_amount: 0,
      it_amount: 0,
      gst_amount: 0,
      lc_amount: 0,
      net_payable: 0,
      payable_words: ""
    }
  };
}
