// User type
export interface User {
  id: string;
  name: string;
  email: string;
}

// Authentication credentials
export interface LoginCredentials {
  email: string;
  password?: string;
}

export interface SignUpCredentials extends LoginCredentials {
  name: string;
}

// Garden types
export interface Garden {
  id: string;
  name: string;
  description: string;
  plantIds: string[];
}

// Plant types
export interface Plant {
  id: string;
  name: string;
  species: string;
  plantingDate: string;
}
