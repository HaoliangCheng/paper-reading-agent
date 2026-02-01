// Dynamic stage item (new format)
export interface ReadingPlanItem {
  id: string;              // Stage ID (e.g., "quick_scan", "methodology")
  title: string;
  description: string;
  key_topics: string[];
  sections?: string[];     // For section_explorer: list of explorable sections
  step?: number;           // Legacy: step number (for backward compatibility)
}

// Content analysis from Step 1
export interface ContentAnalysis {
  sections: string[];
  has_math: boolean;
  has_figures: boolean;
  has_code: boolean;
  is_multi_section: boolean;
}

export interface Paper {
  id: string;
  title: string;
  file_path: string;
  language: string;
  timestamp: string;
  summary?: string;
  reading_plan?: ReadingPlanItem[];
  content_analysis?: ContentAnalysis;
}

export interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: string;
}

export interface UserProfile {
  name: string;
  key_points: string[];
}
