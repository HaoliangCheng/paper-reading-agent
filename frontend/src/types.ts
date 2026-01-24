export interface Paper {
  id: string;
  title: string;
  file_path: string;
  language: string;
  timestamp: string;
  summary?: string;
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
