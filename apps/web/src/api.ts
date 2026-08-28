const API_BASE_URL = "http://127.0.0.1:8001";

export interface Organization {
  id: string;
  name: string;
}

export interface OrganizationCreate {
  name: string;
}

export interface Farm {
  id: string;
  organization_id: string;
  name: string;
  latitude: number;
  longitude: number;
  area_hectares: number;
}

export interface FarmCreate {
  organization_id: string;
  name: string;
  latitude: number;
  longitude: number;
  area_hectares: number;
}

export interface Field {
  id: string;
  farm_id: string;
  name: string;
  area_hectares: number;
  soil_type: string | null;
}

export interface FieldCreate {
  farm_id: string;
  name: string;
  area_hectares: number;
  soil_type: string | null;
}

export interface Observation {
  id: string;
  field_id: string;
  observed_at: string;
  soil_moisture: number | null;
  soil_temperature: number | null;
  air_temperature: number | null;
  humidity: number | null;
  rainfall_mm: number | null;
  source: string;
  created_at: string;
}

export interface ObservationCreate {
  field_id: string;
  observed_at: string;
  soil_moisture: number | null;
  soil_temperature: number | null;
  air_temperature: number | null;
  humidity: number | null;
  rainfall_mm: number | null;
  source: string;
}

export interface Prediction {
  field_id: string;
  observed_at: string;
  crop: string;
  soil_type: string | null;
  crop_stage: number;
  soil_moisture: number | null;
  rainfall_mm: number | null;
  predicted_class: string;
  confidence: number;
  probabilities: Record<string, number>;
  recommended_irrigation_mm: number;
  action: string;
  urgency: string;
  reasons: string[];
}

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(
    `${API_BASE_URL}${path}`,
    {
      headers: {
        "Content-Type": "application/json",
        ...(options?.headers ?? {}),
      },
      ...options,
    },
  );

  if (!response.ok) {
    let message = `Request failed (${response.status})`;

    try {
      const error = await response.json();

      if (typeof error.detail === "string") {
        message = error.detail;
      }
    } catch {
      // Keep default message.
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

/* Organizations */

export function getOrganizations(): Promise<
  Organization[]
> {
  return request<Organization[]>(
    "/api/v1/organizations",
  );
}

export function createOrganization(
  payload: OrganizationCreate,
): Promise<Organization> {
  return request<Organization>(
    "/api/v1/organizations",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

/* Farms */

export function getFarms(): Promise<Farm[]> {
  return request<Farm[]>(
    "/api/v1/farms",
  );
}

export function createFarm(
  payload: FarmCreate,
): Promise<Farm> {
  return request<Farm>(
    "/api/v1/farms",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

/* Fields */

export function getFields(): Promise<Field[]> {
  return request<Field[]>(
    "/api/v1/fields",
  );
}

export function createField(
  payload: FieldCreate,
): Promise<Field> {
  return request<Field>(
    "/api/v1/fields",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

/* Observations */

export function createObservation(
  payload: ObservationCreate,
): Promise<Observation> {
  return request<Observation>(
    "/api/v1/observations",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

/* AI prediction */

export function getIrrigationPrediction(
  fieldId: string,
): Promise<Prediction> {
  return request<Prediction>(
    `/api/v1/predictions/fields/${fieldId}/irrigation`,
  );
}

export { API_BASE_URL };
