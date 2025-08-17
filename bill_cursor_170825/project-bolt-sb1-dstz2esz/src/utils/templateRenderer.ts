import { BillData } from '../types/BillData';

export class TemplateRenderer {
  private static formatNumber(value: number | undefined): string {
    if (value === undefined || value === null) return '';
    return Math.round(value).toString();
  }

  private static formatDecimal(value: number | undefined, decimals: number = 2): string {
    if (value === undefined || value === null) return '';
    return value.toFixed(decimals);
  }

  private static formatDate(dateStr: string): string {
    if (!dateStr) return '';
    // Check if it's in YYYY-MM-DD format and convert to DD/MM/YYYY
    if (dateStr.length >= 10 && dateStr[4] === '-' && dateStr[7] === '-') {
      const year = dateStr.substring(0, 4);
      const month = dateStr.substring(5, 7);
      const day = dateStr.substring(8, 10);
      if (parseInt(year) > 0 && parseInt(month) > 0 && parseInt(day) > 0) {
        return `${day}/${month}/${year}`;
      }
    }
    return dateStr;
  }

  static renderFirstPage(data: BillData): string {
    let html = `
      <div class="bill-page">
        <h1>CONTRACTOR BILL</h1>
    `;

    // Render header information
    if (data.header && data.header.length > 0) {
      data.header.forEach(row => {
        if (row.length > 0) {
          html += '<p>';
          row.forEach(item => {
            if (item && item.trim()) {
              const trimmed = item.trim();
              html += this.formatDate(trimmed) + ' ';
            }
          });
          html += '</p>';
        }
      });
    } else {
      html += `
        <p>Agreement No: ${data.agreement_no}</p>
        <p>Name of Work: ${data.name_of_work}</p>
        <p>Name of Firm: ${data.name_of_firm}</p>
        <p>Date of Commencement: ${this.formatDate(data.date_commencement)}</p>
        <p>Schedule Date of Completion: ${this.formatDate(data.date_completion)}</p>
        <p>Actual Date of Completion: ${this.formatDate(data.actual_completion)}</p>
      `;
    }

    // Main table
    html += `
      <table border="1" style="width: 100%; border-collapse: collapse;">
        <tr>
          <th>Unit</th>
          <th>Quantity executed (or supplied) since last certificate</th>
          <th>Quantity executed (or supplied) up to date as per MB</th>
          <th>Item No.</th>
          <th>Item of Work supplies (Grouped under "sub-head" and "sub work" of estimate)</th>
          <th>Rate</th>
          <th>Amount up to date</th>
          <th>Amount Since previous bill (Total for each sub-head)</th>
          <th>Remark</th>
        </tr>
    `;

    // Bill items
    data.bill_items.forEach(item => {
      html += `
        <tr>
          <td>${item.unit}</td>
          <td>${this.formatDecimal(item.quantity_bill)}</td>
          <td>${this.formatDecimal(item.quantity_bill)}</td>
          <td>${item.serial_no}</td>
          <td>${item.description}</td>
          <td>${this.formatDecimal(item.rate)}</td>
          <td>${this.formatDecimal(item.amount_bill)}</td>
          <td>${this.formatDecimal(item.amount_bill)}</td>
          <td>${item.remark || ''}</td>
        </tr>
      `;
    });

    // Extra items section
    if (data.extra_items && data.extra_items.length > 0) {
      html += `
        <tr>
          <td colspan="9"><strong>Extra Items</strong></td>
        </tr>
      `;

      data.extra_items.forEach(item => {
        html += `
          <tr>
            <td>${item.unit}</td>
            <td>${this.formatDecimal(item.quantity)}</td>
            <td>${this.formatDecimal(item.quantity)}</td>
            <td>${item.serial_no}</td>
            <td>${item.description}</td>
            <td>${this.formatDecimal(item.rate)}</td>
            <td>${this.formatDecimal(item.amount)}</td>
            <td>${this.formatDecimal(item.amount)}</td>
            <td>${item.remark}</td>
          </tr>
        `;
      });

      html += `
        <tr>
          <td colspan="6"><strong>Extra Items Total Rs.</strong></td>
          <td>${data.extra_items_base > 0 ? this.formatDecimal(data.extra_items_base) : 'NIL'}</td>
          <td></td>
          <td></td>
        </tr>
        <tr>
          <td colspan="6"><strong>Tender Premium @ ${(data.tender_premium_percent * 100).toFixed(2)}%</strong></td>
          <td>${data.extra_premium > 0 ? this.formatDecimal(data.extra_premium) : 'NIL'}</td>
          <td></td>
          <td></td>
        </tr>
        <tr>
          <td colspan="6"><strong>Extra Items Grand Total (including Tender Premium) Rs.</strong></td>
          <td>${data.extra_items_sum > 0 ? this.formatDecimal(data.extra_items_sum) : 'NIL'}</td>
          <td></td>
          <td></td>
        </tr>
      `;
    }

    // Totals
    html += `
        <tr>
          <td colspan="6"><strong>Main Items Grand Total Rs.</strong></td>
          <td>${this.formatDecimal(data.bill_total)}</td>
          <td></td>
          <td></td>
        </tr>
        <tr>
          <td colspan="6"><strong>Tender Premium @ ${(data.tender_premium_percent * 100).toFixed(2)}%</strong></td>
          <td>${this.formatDecimal(data.bill_premium)}</td>
          <td></td>
          <td></td>
        </tr>
        <tr>
          <td colspan="6"><strong>Total Payable Amount Rs.</strong></td>
          <td>${this.formatDecimal(data.bill_grand_total + data.extra_items_sum)}</td>
          <td></td>
          <td></td>
        </tr>
      </table>
      </div>
    `;

    return html;
  }

  static renderCertificateII(data: BillData): string {
    return `
      <div class="certificate-page">
        <h2 style="text-align: center; text-decoration: underline;">II. CERTIFICATE AND SIGNATURES</h2>
        
        <div style="text-align: justify; margin-bottom: 15px;">
          <p>The measurements on which are based the entries in columns 1 to 6 of Account I, were made by <span style="border-bottom: 1px dashed #000; padding-bottom: 2px; min-width: 100px; display: inline-block;">${data.measurement_officer}</span> on <span style="border-bottom: 1px dashed #000; padding-bottom: 2px; min-width: 100px; display: inline-block;">${this.formatDate(data.measurement_date)}</span>, and are recorded at page <span style="border-bottom: 1px dashed #000; padding-bottom: 2px; min-width: 100px; display: inline-block;">${data.measurement_book_page}</span> of Measurement Book No. <span style="border-bottom: 1px dashed #000; padding-bottom: 2px; min-width: 100px; display: inline-block;">${data.measurement_book_no}</span></p>
          
          <p>*Certified that in addition to and quite apart from the quantities of work actually executed, as shown in column 4 of Account I, some work has actually been done in connection with several items and the value of such work (after deduction therefrom the proportionate amount of secured advances, if any, ultimately recoverable on account of the quantities of materials used therein) is in no case, less than the advance payments as per item 2 of the Memorandum, if payment is made.</p>
          
          <p>+Certified that the contractor has made satisfactory progress with the work, and that the quantities and amounts claimed are correct and the work has been executed in accordance with the specifications and the terms of the contract.</p>
          
          <p>I also certify that the amount claimed is not more than the amount admissible under the contract.</p>
        </div>
        
        <div style="margin-top: 40px; text-align: right;">
          <p><span style="border-bottom: 1px solid #000; width: 200px; margin: 10px 0; display: inline-block;"></span></p>
          <p>Dated signature of officer preparing the bill</p>
          <p>${data.officer_name}</p>
          <p>${data.officer_designation}</p>
          
          <br><br>
          
          <p><span style="border-bottom: 1px solid #000; width: 200px; margin: 10px 0; display: inline-block;"></span></p>
          <p>+Dated signature of officer authorising payment</p>
          <p>${data.authorising_officer_name}</p>
          <p>${data.authorising_officer_designation}</p>
        </div>
      </div>
    `;
  }

  static renderCertificateIII(data: BillData): string {
    return `
      <div class="certificate-page">
        <h2 style="text-align: center; text-decoration: underline;">III. MEMORANDUM OF PAYMENTS</h2>

        <table border="1" style="width: 100%; border-collapse: collapse; font-size: 9pt;">
          <thead>
            <tr>
              <th style="width: 8%;">S.No.</th>
              <th style="width: 60%;">Description</th>
              <th style="width: 12%;">Entry No.</th>
              <th style="width: 20%;">Amount Rs.</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>1.</td>
              <td>Total value of work actually measured, as per Account I, Col. 5, Entry [A]</td>
              <td style="text-align: center;">[A]</td>
              <td style="text-align: right;">${this.formatNumber(data.totals.grand_total)}</td>
            </tr>
            <tr>
              <td>2.</td>
              <td>Total up-to-date advance payments for work not yet measured as per details given below:</td>
              <td></td>
              <td></td>
            </tr>
            <tr>
              <td></td>
              <td style="padding-left: 20px;">(a) Total as per previous bill</td>
              <td style="text-align: center;">[B]</td>
              <td style="text-align: right;">Nil</td>
            </tr>
            <tr>
              <td></td>
              <td style="padding-left: 20px;">(b) Since previous bill</td>
              <td style="text-align: center;">[D]</td>
              <td style="text-align: right;">Nil</td>
            </tr>
            <tr>
              <td>3.</td>
              <td>Total up-to-date secured advances on security of materials</td>
              <td style="text-align: center;">[C]</td>
              <td style="text-align: right;">Nil</td>
            </tr>
            <tr>
              <td>4.</td>
              <td style="font-weight: bold;">Total (Items 1 + 2 + 3) A+B+C</td>
              <td></td>
              <td style="text-align: right; font-weight: bold;">${this.formatNumber(data.totals.grand_total)}</td>
            </tr>
            <tr>
              <td colspan="4" style="font-weight: bold; text-align: center; text-decoration: underline;">Figures for works abstract</td>
            </tr>
            <tr>
              <td>5.</td>
              <td colspan="3" style="font-weight: bold;">Deduct: Amount withheld</td>
            </tr>
            <tr>
              <td></td>
              <td>(a) From previous bill as per last Running Account Bill</td>
              <td style="text-align: center;">[5]</td>
              <td style="text-align: right;">Nil</td>
            </tr>
            <tr>
              <td></td>
              <td>(b) From this bill</td>
              <td></td>
              <td style="text-align: right;">Nil</td>
            </tr>
            <tr>
              <td>6.</td>
              <td style="font-weight: bold;">Balance i.e. "up-to-date" payments (Item 4-5)</td>
              <td></td>
              <td style="text-align: right; font-weight: bold;">${this.formatNumber(data.totals.grand_total)}</td>
            </tr>
            <tr>
              <td>7.</td>
              <td>Total amount of payments already made as per Entry (K)</td>
              <td style="text-align: center;">[K]</td>
              <td style="text-align: right;">0</td>
            </tr>
            <tr>
              <td>8.</td>
              <td style="font-weight: bold;">Payments now to be made, as detailed below:</td>
              <td></td>
              <td style="text-align: right; font-weight: bold;">${this.formatNumber(data.totals.net_payable)}</td>
            </tr>
            <tr>
              <td></td>
              <td>(a) By recovery of amounts creditable to this work</td>
              <td style="text-align: center;">[a]</td>
              <td></td>
            </tr>
            <tr>
              <td></td>
              <td style="padding-left: 20px;">SD @ 10%</td>
              <td></td>
              <td style="text-align: right;">${this.formatNumber(data.totals.sd_amount)}</td>
            </tr>
            <tr>
              <td></td>
              <td style="padding-left: 20px;">IT @ 2%</td>
              <td></td>
              <td style="text-align: right;">${this.formatNumber(data.totals.it_amount)}</td>
            </tr>
            <tr>
              <td></td>
              <td style="padding-left: 20px;">GST @ 2%</td>
              <td></td>
              <td style="text-align: right;">${this.formatNumber(data.totals.gst_amount)}</td>
            </tr>
            <tr>
              <td></td>
              <td style="padding-left: 20px;">LC @ 1%</td>
              <td></td>
              <td style="text-align: right;">${this.formatNumber(data.totals.lc_amount)}</td>
            </tr>
            <tr>
              <td></td>
              <td style="padding-left: 20px;">Total recovery</td>
              <td></td>
              <td style="text-align: right;">${this.formatNumber(data.totals.total_deductions)}</td>
            </tr>
            <tr>
              <td></td>
              <td>(b) By recovery of amount creditable to other works</td>
              <td style="text-align: center;">[b]</td>
              <td style="text-align: right;">Nil</td>
            </tr>
            <tr>
              <td></td>
              <td style="font-weight: bold;">(c) By cheque</td>
              <td style="text-align: center;">[c]</td>
              <td style="text-align: right; font-weight: bold;">${this.formatNumber(data.totals.net_payable)}</td>
            </tr>
          </tbody>
        </table>

        <div style="margin-top: 20px; padding: 10px; border: 1px solid #000;">
          <p style="font-weight: bold;">Pay Rs. ${this.formatNumber(data.totals.net_payable)}</p>
          <p>Pay Rupees ${data.payable_words} (by cheque)</p>
          <br>
          <p>Dated the _____ 20____</p>
          <p style="text-align: right;">Dated initials of Disbursing Officer</p>
          <br>
          <p>Received Rupees ${data.payable_words} (by cheque) as per above memorandum, on account of this bill</p>
          <br>
          <p style="text-align: right;">Signature of Contractor</p>
          <br>
          <p>Paid by me, vide cheque No. _______ dated _____ 20____</p>
          <p style="text-align: right;">Dated initials of person actually making the payment</p>
        </div>
      </div>
    `;
  }

  static renderDeviationStatement(data: BillData): string {
    let html = `
      <div class="deviation-page">
        <h1>DEVIATION STATEMENT</h1>
    `;

    // Header information
    if (data.header && data.header.length > 0) {
      data.header.forEach(row => {
        if (row.length > 0) {
          html += '<p>';
          row.forEach(item => {
            if (item && item.trim()) {
              html += this.formatDate(item.trim()) + ' ';
            }
          });
          html += '</p>';
        }
      });
    } else {
      html += `
        <p>Agreement No: ${data.agreement_no}</p>
        <p>Name of Work: ${data.name_of_work}</p>
        <p>Name of Firm: ${data.name_of_firm}</p>
        <p>Date of Commencement: ${this.formatDate(data.date_commencement)}</p>
        <p>Schedule Date of Completion: ${this.formatDate(data.date_completion)}</p>
        <p>Actual Date of Completion: ${this.formatDate(data.actual_completion)}</p>
      `;
    }

    html += `
      <table border="1" style="width: 100%; border-collapse: collapse;">
        <tr>
          <th>Item No.</th>
          <th>Item of Work</th>
          <th>Unit</th>
          <th>Qty as per Work Order</th>
          <th>Rate</th>
          <th>Amount as per Work Order</th>
          <th>Qty as Executed</th>
          <th>Amount as Executed</th>
          <th>Excess Qty</th>
          <th>Excess Amount</th>
          <th>Saving Qty</th>
          <th>Saving Amount</th>
          <th>Remark</th>
        </tr>
    `;

    data.deviation_items.forEach(item => {
      html += `
        <tr>
          <td>${item.serial_no}</td>
          <td>${item.description}</td>
          <td>${item.unit}</td>
          <td>${item.qty_wo ? this.formatDecimal(item.qty_wo) : ''}</td>
          <td>${item.rate ? this.formatDecimal(item.rate) : ''}</td>
          <td>${item.amt_wo ? this.formatDecimal(item.amt_wo) : ''}</td>
          <td>${item.qty_bill ? this.formatDecimal(item.qty_bill) : ''}</td>
          <td>${item.amt_bill ? this.formatDecimal(item.amt_bill) : ''}</td>
          <td>${item.excess_qty ? this.formatDecimal(item.excess_qty) : ''}</td>
          <td>${item.excess_amt ? this.formatDecimal(item.excess_amt) : ''}</td>
          <td>${item.saving_qty ? this.formatDecimal(item.saving_qty) : ''}</td>
          <td>${item.saving_amt ? this.formatDecimal(item.saving_amt) : ''}</td>
          <td>${item.remark}</td>
        </tr>
      `;
    });

    // Summary section
    const summary = data.deviation_summary;
    html += `
        <tr>
          <td colspan="13"><strong>Summary</strong></td>
        </tr>
        <tr>
          <td colspan="5"><strong>Total Work Order Amount</strong></td>
          <td>${this.formatDecimal(summary.work_order_total)}</td>
          <td colspan="7"></td>
        </tr>
        <tr>
          <td colspan="5"><strong>Tender Premium @ ${(data.tender_premium_percent * 100).toFixed(2)}%</strong></td>
          <td>${this.formatDecimal(summary.tender_premium_f)}</td>
          <td colspan="7"></td>
        </tr>
        <tr>
          <td colspan="5"><strong>Grand Total Work Order</strong></td>
          <td>${this.formatDecimal(summary.grand_total_f)}</td>
          <td colspan="7"></td>
        </tr>
        <tr>
          <td colspan="7"><strong>Total Executed Amount</strong></td>
          <td>${this.formatDecimal(summary.executed_total)}</td>
          <td colspan="5"></td>
        </tr>
        <tr>
          <td colspan="7"><strong>Tender Premium @ ${(data.tender_premium_percent * 100).toFixed(2)}%</strong></td>
          <td>${this.formatDecimal(summary.tender_premium_h)}</td>
          <td colspan="5"></td>
        </tr>
        <tr>
          <td colspan="7"><strong>Grand Total Executed</strong></td>
          <td>${this.formatDecimal(summary.grand_total_h)}</td>
          <td colspan="5"></td>
        </tr>
        <tr>
          <td colspan="9"><strong>Excess</strong></td>
          <td colspan="4"></td>
        </tr>
        <tr>
          <td colspan="9"><strong>Total Excess Amount</strong></td>
          <td>${this.formatDecimal(summary.overall_excess)}</td>
          <td colspan="3"></td>
        </tr>
        <tr>
          <td colspan="9"><strong>Tender Premium @ ${(data.tender_premium_percent * 100).toFixed(2)}%</strong></td>
          <td>${this.formatDecimal(summary.tender_premium_j)}</td>
          <td colspan="3"></td>
        </tr>
        <tr>
          <td colspan="9"><strong>Grand Total Excess</strong></td>
          <td>${this.formatDecimal(summary.grand_total_j)}</td>
          <td colspan="3"></td>
        </tr>
        <tr>
          <td colspan="11"><strong>Saving</strong></td>
          <td colspan="2"></td>
        </tr>
        <tr>
          <td colspan="11"><strong>Total Saving Amount</strong></td>
          <td>${this.formatDecimal(summary.overall_saving)}</td>
          <td></td>
        </tr>
        <tr>
          <td colspan="11"><strong>Tender Premium @ ${(data.tender_premium_percent * 100).toFixed(2)}%</strong></td>
          <td>${this.formatDecimal(summary.tender_premium_l)}</td>
          <td></td>
        </tr>
        <tr>
          <td colspan="11"><strong>Grand Total Saving</strong></td>
          <td>${this.formatDecimal(summary.grand_total_l)}</td>
          <td></td>
        </tr>
        <tr>
          <td colspan="11"><strong>Net Difference</strong></td>
          <td>${this.formatDecimal(summary.net_difference)}</td>
          <td></td>
        </tr>
      </table>
      </div>
    `;

    return html;
  }

  static renderExtraItems(data: BillData): string {
    return `
      <div class="extra-items-page">
        <div style="text-align: center;">
          <h2>Extra Items</h2>
        </div>
        <table border="1" style="width: 100%; border-collapse: collapse;">
          <thead>
            <tr>
              <th>Serial No.</th>
              <th>Remark</th>
              <th>Description</th>
              <th>Quantity</th>
              <th>Unit</th>
              <th>Rate</th>
              <th>Amount</th>
            </tr>
          </thead>
          <tbody>
            ${data.extra_items && data.extra_items.length > 0 
              ? data.extra_items.map(item => `
                <tr>
                  <td>${item.serial_no}</td>
                  <td>${item.remark}</td>
                  <td>${item.description}</td>
                  <td>${item.quantity ? this.formatNumber(item.quantity) : ''}</td>
                  <td>${item.unit}</td>
                  <td>${item.rate ? this.formatNumber(item.rate) : ''}</td>
                  <td>${item.amount ? this.formatNumber(item.amount) : ''}</td>
                </tr>
              `).join('')
              : `
                <tr>
                  <td colspan="7" style="text-align: center; font-style: italic;">No extra items</td>
                </tr>
              `
            }
          </tbody>
        </table>
      </div>
    `;
  }
}