import { BillData } from '../types/BillData';

export const generateSampleBillData = (): BillData => {
  return {
    agreement_no: "PWD/2024/RD/001",
    name_of_work: "Construction of 4-lane Highway Bridge over River XYZ",
    name_of_firm: "Modern Infrastructure Pvt. Ltd.",
    date_commencement: "2024-01-15",
    date_completion: "2024-12-15",
    actual_completion: "2024-11-30",
    
    bill_items: [
      {
        serial_no: "1.1",
        description: "Excavation in ordinary soil for foundation including dressing and leveling",
        unit: "Cum",
        quantity_bill: 2450.75,
        rate: 285.50,
        amount_bill: 699589.13,
        remark: "As per IS:1200 Part-VIII"
      },
      {
        serial_no: "1.2",
        description: "Plain Cement Concrete 1:2:4 for foundation",
        unit: "Cum",
        quantity_bill: 185.25,
        rate: 4750.00,
        amount_bill: 879937.50,
        remark: "M15 Grade as per IS:456"
      },
      {
        serial_no: "2.1",
        description: "Reinforced Cement Concrete 1:1.5:3 for superstructure",
        unit: "Cum",
        quantity_bill: 125.80,
        rate: 6850.00,
        amount_bill: 861730.00,
        remark: "M25 Grade with TMT bars"
      },
      {
        serial_no: "3.1",
        description: "Providing and laying bituminous concrete wearing course",
        unit: "Cum",
        quantity_bill: 95.50,
        rate: 8500.00,
        amount_bill: 811750.00,
        remark: "Grade-1 as per MORTH"
      }
    ],
    
    extra_items: [
      {
        serial_no: "E1",
        remark: "Site condition variation",
        description: "Additional dewatering arrangement due to high water table",
        quantity: 15.0,
        unit: "Days",
        rate: 12500.00,
        amount: 187500.00
      },
      {
        serial_no: "E2", 
        remark: "Design modification",
        description: "Extra reinforcement steel for seismic strengthening",
        quantity: 3.25,
        unit: "MT",
        rate: 68000.00,
        amount: 221000.00
      }
    ],
    
    deviation_items: [
      {
        serial_no: "1.1",
        description: "Excavation in ordinary soil for foundation",
        unit: "Cum",
        qty_wo: 2200.00,
        rate: 285.50,
        amt_wo: 628100.00,
        qty_bill: 2450.75,
        amt_bill: 699589.13,
        excess_qty: 250.75,
        excess_amt: 71489.13,
        saving_qty: 0,
        saving_amt: 0,
        remark: "Additional excavation due to rock strata"
      },
      {
        serial_no: "2.1",
        description: "Reinforced Cement Concrete for superstructure",
        unit: "Cum", 
        qty_wo: 140.00,
        rate: 6850.00,
        amt_wo: 959000.00,
        qty_bill: 125.80,
        amt_bill: 861730.00,
        excess_qty: 0,
        excess_amt: 0,
        saving_qty: 14.20,
        saving_amt: 97270.00,
        remark: "Optimized design reduced concrete requirement"
      }
    ],
    
    bill_total: 3253006.63,
    bill_premium: 162650.33,
    bill_grand_total: 3415656.96,
    extra_items_base: 408500.00,
    extra_premium: 20425.00,
    extra_items_sum: 428925.00,
    tender_premium_percent: 0.05,
    
    deviation_summary: {
      work_order_total: 1587100.00,
      tender_premium_f: 79355.00,
      grand_total_f: 1666455.00,
      executed_total: 1561319.13,
      tender_premium_h: 78065.96,
      grand_total_h: 1639385.09,
      overall_excess: 71489.13,
      tender_premium_j: 3574.46,
      grand_total_j: 75063.59,
      overall_saving: 97270.00,
      tender_premium_l: 4863.50,
      grand_total_l: 102133.50,
      net_difference: -27069.91
    },
    
    totals: {
      grand_total: 3844581.96,
      sd_amount: 384458.20,
      it_amount: 76891.64,
      gst_amount: 76891.64,
      lc_amount: 38445.82,
      total_deductions: 576687.30,
      net_payable: 3267894.66
    },
    
    measurement_officer: "Rajesh Kumar, Assistant Engineer",
    measurement_date: "2024-11-25",
    measurement_book_page: "127-135",
    measurement_book_no: "MB-PWD-2024-45",
    officer_name: "Priya Sharma",
    officer_designation: "Assistant Engineer (Civil)",
    authorising_officer_name: "Suresh Patel",
    authorising_officer_designation: "Executive Engineer",
    
    payable_words: "Thirty Two Lakh Sixty Seven Thousand Eight Hundred Ninety Four and Sixty Six Paise Only",
    
    header: [
      ["PWD Division: Highway Construction Division-III"],
      ["Sub-Division: Bridge Construction Sub-Division"],
      ["Bill No: RB/2024/001", "Date: 2024-11-30"],
      ["Running Account Bill No: 3", "Period: October 2024"]
    ]
  };
};
</parameter>