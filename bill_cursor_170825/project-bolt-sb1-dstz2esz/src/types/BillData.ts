export interface BillItem {
  serial_no: string;
  description: string;
  unit: string;
  quantity_bill: number;
  rate: number;
  amount_bill: number;
  remark?: string;
}

export interface ExtraItem {
  serial_no: string;
  remark: string;
  description: string;
  quantity: number;
  unit: string;
  rate: number;
  amount: number;
}

export interface DeviationItem {
  serial_no: string;
  description: string;
  unit: string;
  qty_wo: number;
  rate: number;
  amt_wo: number;
  qty_bill: number;
  amt_bill: number;
  excess_qty: number;
  excess_amt: number;
  saving_qty: number;
  saving_amt: number;
  remark: string;
}

export interface DeviationSummary {
  work_order_total: number;
  tender_premium_f: number;
  grand_total_f: number;
  executed_total: number;
  tender_premium_h: number;
  grand_total_h: number;
  overall_excess: number;
  tender_premium_j: number;
  grand_total_j: number;
  overall_saving: number;
  tender_premium_l: number;
  grand_total_l: number;
  net_difference: number;
}

export interface BillTotals {
  grand_total: number;
  sd_amount: number;
  it_amount: number;
  gst_amount: number;
  lc_amount: number;
  total_deductions: number;
  net_payable: number;
}

export interface BillData {
  // Header information
  agreement_no: string;
  name_of_work: string;
  name_of_firm: string;
  date_commencement: string;
  date_completion: string;
  actual_completion: string;
  
  // Bill items
  bill_items: BillItem[];
  extra_items: ExtraItem[];
  deviation_items: DeviationItem[];
  
  // Calculations
  bill_total: number;
  bill_premium: number;
  bill_grand_total: number;
  extra_items_base: number;
  extra_premium: number;
  extra_items_sum: number;
  tender_premium_percent: number;
  
  // Summaries
  deviation_summary: DeviationSummary;
  totals: BillTotals;
  
  // Certificate data
  measurement_officer: string;
  measurement_date: string;
  measurement_book_page: string;
  measurement_book_no: string;
  officer_name: string;
  officer_designation: string;
  authorising_officer_name: string;
  authorising_officer_designation: string;
  
  // Payment
  payable_words: string;
  
  // Optional header array for dynamic content
  header?: string[][];
}
</parameter>