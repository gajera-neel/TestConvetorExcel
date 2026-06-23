export type ExtractedFields = {
  columns: string[];
  rows: Record<string, string>[];
  fields: Record<string, string>;
  detected_type: string;
};

export type UploadResult = {
  id: string;
  filename: string;
  file_type: string;
  detected_type: string;
  extracted_text: string;
  extracted_fields: ExtractedFields;
  confidence: number;
  logs: string[];
  preview_url?: string;
  dashboard: DashboardData;
};

export type DashboardData = {
  mode?: "global" | "single";
  bill_id?: string;
  metrics: {
    uploads: number;
    bills: number;
    success_rate: number;
    total_records: number;
    total_uploads?: number;
    total_bills?: number;
    total_amount?: string;
    total_tax?: string;
    average_bill_amount?: string;
    highest_bill_amount?: string;
    unique_vendors?: number;
    todays_uploads?: number;
  };
  uploads_by_day?: ChartPoint[];
  amount_trend?: ChartPoint[];
  bill_categories?: ChartPoint[];
  extraction_activity: ChartPoint[];
  file_types: ChartPoint[];
  data_volume: ChartPoint[];
  top_vendors?: ChartPoint[];
  amount_breakdown?: ChartPoint[];
  recent_uploads: RecentUpload[];
  uploaded_bills?: UploadedBill[];
  bill?: BillDashboardDetail;
  summary?: SummaryItem[];
  calculation_issues?: CalculationIssue[];
};

export type ChartPoint = {
  label?: string;
  day?: string;
  detected_type?: string;
  value?: number;
  count?: number;
  amount?: string;
};

export type RecentUpload = {
  id?: string;
  filename: string;
  detected_type: string;
  confidence?: number;
  uploaded_at: string;
  vendor?: string;
  amount?: string;
  rows_count?: number;
};

export type UploadedBill = {
  id: string;
  filename: string;
  bill_name?: string;
  uploaded_at: string;
  file_type: string;
  detected_type: string;
  amount: string;
  vendor: string;
  status: string;
  confidence?: number;
  rows_count?: number;
  calculation_status?: "balanced" | "needs_review";
  calculation_issues?: string[];
};

export type BillDashboardDetail = UploadedBill & {
  fields: Record<string, string>;
  rows: Record<string, string>[];
  columns: string[];
  extracted_text: string;
  preview_url?: string;
  invoice_number?: string;
  bill_date?: string;
  customer?: string;
  tax?: string;
  total?: string;
  calculation?: CalculationAudit;
  raw_json?: Record<string, unknown>;
};

export type SummaryItem = {
  label: string;
  value: string | number;
};

export type CalculationAudit = {
  subtotal: string;
  tax: string;
  discount: string;
  total: string;
  expected_total: string;
  difference: string;
  is_balanced: boolean;
  issues: string[];
  sources: Record<string, string>;
  raw_fields: Record<string, string>;
  raw_rows: Record<string, string>[];
};

export type CalculationIssue = {
  id?: string;
  filename?: string;
  audit: CalculationAudit;
};
