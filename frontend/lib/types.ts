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
  metrics: {
    uploads: number;
    bills: number;
    success_rate: number;
    total_records: number;
    total_uploads?: number;
    total_bills?: number;
    total_amount?: string;
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
  recent_uploads: RecentUpload[];
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
