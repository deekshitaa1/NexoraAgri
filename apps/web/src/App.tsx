import { useEffect, useMemo, useState } from "react";
import "./App.css";

const API_BASE = "http://127.0.0.1:8001";

type Page =
  | "dashboard"
  | "fields"
  | "irrigation"
  | "observations"
  | "alerts"
  | "reports"
  | "settings";

type Field = {
  id: string;
  farm_id: string;
  name: string;
  area_hectares: number;
  soil_type: string | null;
};

type Farm = {
  id: string;
  organization_id: string;
  name: string;
  latitude: number | null;
  longitude: number | null;
  area_hectares: number;
};

type Observation = {
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
};

type Prediction = {
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
};

const navItems: { id: Page; label: string; icon: string }[] = [
  { id: "dashboard", label: "Dashboard", icon: "D" },
  { id: "fields", label: "Fields", icon: "F" },
  { id: "irrigation", label: "Irrigation Intelligence", icon: "I" },
  { id: "observations", label: "Observations", icon: "O" },
  { id: "alerts", label: "Alerts", icon: "A" },
  { id: "reports", label: "Reports", icon: "R" },
  { id: "settings", label: "Settings", icon: "S" },
];

async function api<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let message = `Request failed (${response.status})`;

    try {
      const body = await response.json();

      if (body?.detail) {
        message = body.detail;
      }
    } catch {
      // Keep HTTP error message.
    }

    throw new Error(message);
  }

  return response.json();
}

function App() {
  const [page, setPage] = useState<Page>("dashboard");

  const [fields, setFields] = useState<Field[]>([]);
  const [farms, setFarms] = useState<Farm[]>([]);
  const [observations, setObservations] = useState<Observation[]>([]);
  const [prediction, setPrediction] = useState<Prediction | null>(null);

  const [selectedField, setSelectedField] = useState("");
  const [loading, setLoading] = useState(true);
  const [predictionLoading, setPredictionLoading] = useState(false);
  const [error, setError] = useState("");

  const [showAddField, setShowAddField] = useState(false);
  const [showAddObservation, setShowAddObservation] =
    useState(false);

  const selectedFieldData = useMemo(
    () =>
      fields.find(
        (field) => field.id === selectedField,
      ),
    [fields, selectedField],
  );

  async function loadFields() {
    const data = await api<Field[]>(
      "/api/v1/fields",
    );

    setFields(data);

    if (data.length > 0) {
      setSelectedField((current) =>
        current && data.some((field) => field.id === current)
          ? current
          : data[0].id,
      );
    }
  }

  async function loadFarms() {
    const data = await api<Farm[]>(
      "/api/v1/farms",
    );

    setFarms(data);
  }

  async function loadObservations(fieldId: string) {
    /*
      Your current backend only exposes POST /observations.
      Therefore this function intentionally does not call
      GET /observations.

      The newly-created observation is kept in the frontend
      state after POST.
    */

    setObservations((current) =>
      current.filter(
        (observation) =>
          observation.field_id === fieldId,
      ),
    );
  }

  async function loadPrediction(fieldId: string) {
    setPredictionLoading(true);
    setError("");

    try {
      const data = await api<Prediction>(
        `/api/v1/predictions/fields/${fieldId}/irrigation`,
      );

      setPrediction(data);
    } catch (err) {
      setPrediction(null);

      const message =
        err instanceof Error
          ? err.message
          : "Unable to load prediction";

      setError(message);
    } finally {
      setPredictionLoading(false);
    }
  }

  async function refreshAll() {
    setError("");
    setLoading(true);

    try {
      await Promise.all([
        loadFields(),
        loadFarms(),
      ]);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to connect to Nexora Agri API",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refreshAll();
  }, []);

  useEffect(() => {
    if (!selectedField) {
      setPrediction(null);
      return;
    }

    loadPrediction(selectedField);
    loadObservations(selectedField);
  }, [selectedField]);

  const confidence = prediction
    ? `${(prediction.confidence * 100).toFixed(2)}%`
    : "--";

  const irrigation = prediction
    ? prediction.recommended_irrigation_mm.toFixed(2)
    : "--";

  const moisture =
    prediction?.soil_moisture != null
      ? prediction.soil_moisture.toFixed(2)
      : "--";

  const cropStage = prediction
    ? `${Math.round(prediction.crop_stage * 100)}%`
    : "--";

  const predictionClass =
    prediction?.predicted_class ?? "--";

  async function handleObservationCreated(
    observation: Observation,
  ) {
    setObservations((current) => [
      observation,
      ...current.filter(
        (item) => item.id !== observation.id,
      ),
    ]);

    setShowAddObservation(false);

    await loadPrediction(observation.field_id);

    setPage("dashboard");
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <span className="leaf-shape" />
          </div>

          <div>
            <strong>Nexora Agri</strong>
            <small>
              Decision Intelligence
            </small>
          </div>
        </div>

        <nav className="navigation">
          {navItems.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${
                page === item.id ? "active" : ""
              }`}
              onClick={() => setPage(item.id)}
            >
              <span className="nav-icon">
                {item.icon}
              </span>

              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-farm-art">
          <div className="sun-orb" />
          <div className="hill hill-one" />
          <div className="hill hill-two" />
          <div className="field-lines" />
          <div className="tree tree-one" />
          <div className="tree tree-two" />
        </div>

        <div className="sidebar-footer">
          <div className="footer-leaf">
            N
          </div>

          <strong>Nexora Agri</strong>

          <span>
            Smart Decisions, Better Farms
          </span>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <button
            className="menu-button"
            onClick={() => setPage("dashboard")}
          >
            N
          </button>

          <div className="topbar-spacer" />

          <div className="intelligence">
            <div className="status-dot" />

            <div>
              <strong>
                Agri Intelligence
              </strong>

              <small>
                Live field analysis
              </small>
            </div>
          </div>

          <div className="notification">
            <span className="bell">!</span>
            <b>3</b>
          </div>

          <div className="profile">
            <div className="avatar">
              F
            </div>

            <div>
              <strong>
                Farm Manager
              </strong>

              <small>
                Nexora Farm
              </small>
            </div>
          </div>
        </header>

        <div className="content">
          {error && (
            <div className="api-error">
              <strong>
                API issue:
              </strong>

              <span>{error}</span>

              <button
                onClick={refreshAll}
              >
                Retry
              </button>
            </div>
          )}

          {page === "dashboard" && (
            <Dashboard
              fields={fields}
              selectedField={selectedField}
              selectedFieldData={
                selectedFieldData
              }
              prediction={prediction}
              loading={loading}
              predictionLoading={
                predictionLoading
              }
              confidence={confidence}
              irrigation={irrigation}
              moisture={moisture}
              cropStage={cropStage}
              predictionClass={
                predictionClass
              }
              onFieldChange={
                setSelectedField
              }
              onNavigate={setPage}
              onAddObservation={() =>
                setShowAddObservation(true)
              }
            />
          )}

          {page === "fields" && (
            <FieldsPage
              fields={fields}
              farms={farms}
              selectedField={selectedField}
              onSelectField={(id) => {
                setSelectedField(id);
                setPage("dashboard");
              }}
              onAdd={() =>
                setShowAddField(true)
              }
              onRefresh={loadFields}
            />
          )}

          {page === "irrigation" && (
            <IrrigationPage
              field={selectedFieldData}
              prediction={prediction}
              confidence={confidence}
              irrigation={irrigation}
              moisture={moisture}
              cropStage={cropStage}
            />
          )}

          {page === "observations" && (
            <ObservationsPage
              fields={fields}
              observations={
                observations.filter(
                  (item) =>
                    item.field_id ===
                    selectedField,
                )
              }
              selectedField={
                selectedField
              }
              onFieldChange={
                setSelectedField
              }
              onAdd={() =>
                setShowAddObservation(true)
              }
            />
          )}

          {page === "alerts" && (
            <SimplePage
              title="Alerts"
              eyebrow="ATTENTION CENTER"
              description="Decision alerts generated from live field conditions."
            >
              <div className="empty-panel">
                <div className="empty-icon">
                  !
                </div>

                <h3>
                  {prediction?.urgency ===
                  "HIGH"
                    ? "High urgency detected"
                    : "No critical alerts"}
                </h3>

                <p>
                  {prediction?.urgency ===
                  "HIGH"
                    ? prediction.action
                    : "The selected field has no high-urgency irrigation alert."}
                </p>
              </div>
            </SimplePage>
          )}

          {page === "reports" && (
            <SimplePage
              title="Reports"
              eyebrow="FARM REPORTING"
              description="Reports based on real Nexora Agri field and observation data."
            >
              <div className="report-grid">
                <div className="feature-card">
                  <span>01</span>
                  <h3>
                    Irrigation summary
                  </h3>
                  <p>
                    Current recommendation:{" "}
                    {irrigation} mm.
                  </p>
                </div>

                <div className="feature-card">
                  <span>02</span>
                  <h3>
                    Field health
                  </h3>
                  <p>
                    Soil moisture:{" "}
                    {moisture}%.
                  </p>
                </div>

                <div className="feature-card">
                  <span>03</span>
                  <h3>
                    Model confidence
                  </h3>
                  <p>
                    Current confidence:{" "}
                    {confidence}.
                  </p>
                </div>
              </div>
            </SimplePage>
          )}

          {page === "settings" && (
            <SimplePage
              title="Settings"
              eyebrow="SYSTEM"
              description="Nexora Agri connection and workspace settings."
            >
              <div className="settings-panel">
                <div>
                  <strong>
                    API endpoint
                  </strong>

                  <span>
                    {API_BASE}
                  </span>
                </div>

                <div>
                  <strong>
                    Connection
                  </strong>

                  <span className="connected">
                    Live API
                  </span>
                </div>

                <button
                  className="primary-button"
                  onClick={refreshAll}
                >
                  Refresh live data
                </button>
              </div>
            </SimplePage>
          )}

          <footer className="dashboard-footer">
            <span>
              2026 Nexora Agri
            </span>

            <span>
              AI-powered agricultural
              decision intelligence
            </span>

            <span className="api-live">
              <i />
              API Connected
            </span>
          </footer>
        </div>
      </main>

      {showAddField && (
        <AddFieldModal
          farms={farms}
          onClose={() =>
            setShowAddField(false)
          }
          onCreated={async (field) => {
            setFields((current) => [
              field,
              ...current,
            ]);

            setSelectedField(
              field.id,
            );

            setShowAddField(false);
            setPage("fields");
          }}
        />
      )}

      {showAddObservation && (
        <AddObservationModal
          fields={fields}
          selectedField={
            selectedField
          }
          onClose={() =>
            setShowAddObservation(
              false,
            )
          }
          onCreated={
            handleObservationCreated
          }
        />
      )}
    </div>
  );
}

function Dashboard({
  fields,
  selectedField,
  selectedFieldData,
  prediction,
  loading,
  predictionLoading,
  confidence,
  irrigation,
  moisture,
  cropStage,
  predictionClass,
  onFieldChange,
  onNavigate,
  onAddObservation,
}: {
  fields: Field[];
  selectedField: string;
  selectedFieldData?: Field;
  prediction: Prediction | null;
  loading: boolean;
  predictionLoading: boolean;
  confidence: string;
  irrigation: string;
  moisture: string;
  cropStage: string;
  predictionClass: string;
  onFieldChange: (id: string) => void;
  onNavigate: (page: Page) => void;
  onAddObservation: () => void;
}) {
  return (
    <>
      <section className="welcome-row">
        <div>
          <div className="eyebrow">
            NEXORA AGRI / OPERATIONS
          </div>

          <h1>
            Good afternoon
          </h1>

          <p>
            Live agricultural intelligence
            from your field data.
          </p>
        </div>

        <label className="farm-selector">
          <span className="farm-icon">
            F
          </span>

          <span>
            <small>
              Active Field
            </small>

            <strong>
              {selectedFieldData?.name ??
                "No field selected"}
            </strong>
          </span>

          <select
            value={selectedField}
            onChange={(event) =>
              onFieldChange(
                event.target.value,
              )
            }
          >
            {!fields.length && (
              <option value="">
                No fields
              </option>
            )}

            {fields.map((field) => (
              <option
                key={field.id}
                value={field.id}
              >
                {field.name}
              </option>
            ))}
          </select>
        </label>
      </section>

      <section className="metric-grid">
        <MetricCard
          title="Total Fields"
          value={
            loading
              ? "--"
              : String(fields.length)
          }
          subtitle="Registered fields"
          icon="F"
        />

        <MetricCard
          title="Active Crop"
          value={
            prediction ? "1" : "--"
          }
          subtitle={
            prediction?.crop ??
            "No crop analysis"
          }
          icon="C"
        />

        <MetricCard
          title="Irrigation Today"
          value={
            prediction
              ? `${irrigation} mm`
              : "--"
          }
          subtitle="AI recommendation"
          icon="W"
          highlight
        />

        <MetricCard
          title="Confidence"
          value={confidence}
          subtitle="ML model confidence"
          icon="AI"
          highlight
        />
      </section>

      <section className="primary-grid">
        <article className="card irrigation-card">
          <div className="card-heading">
            <div>
              <span className="heading-icon">
                W
              </span>

              <h2>
                Irrigation Recommendation
              </h2>
            </div>

            <span
              className={`status ${predictionClass.toLowerCase()}`}
            >
              {predictionClass}
            </span>
          </div>

          <div className="irrigation-body">
            <Gauge
              prediction={prediction}
              predictionClass={
                predictionClass
              }
            />

            <div className="recommendation-details">
              <span className="detail-label">
                Recommended Irrigation
              </span>

              <div className="big-number">
                {predictionLoading
                  ? "..."
                  : irrigation}

                <small> mm</small>
              </div>

              <div className="recommendation-note">
                {prediction?.action ??
                  "Add a field observation to generate an AI recommendation."}
              </div>

              <DetailRow
                label="Confidence"
                value={confidence}
              />

              <DetailRow
                label="Soil Moisture"
                value={`${moisture}%`}
              />

              <DetailRow
                label="Crop Stage"
                value={cropStage}
              />
            </div>
          </div>

          <button
            className="primary-button observation-cta"
            onClick={onAddObservation}
          >
            + Add New Observation
          </button>
        </article>

        <article className="card reasons-card">
          <div className="card-heading">
            <div>
              <span className="heading-icon">
                AI
              </span>

              <h2>
                Why This Recommendation?
              </h2>
            </div>
          </div>

          <div className="reason-list">
            {prediction?.reasons?.length ? (
              prediction.reasons.map(
                (reason, index) => (
                  <div
                    className="reason"
                    key={`${reason}-${index}`}
                  >
                    <div className="reason-icon">
                      {index + 1}
                    </div>

                    <div>
                      <strong>
                        {index === 0
                          ? "Soil condition"
                          : index === 1
                            ? "Moisture analysis"
                            : "Crop growth stage"}
                      </strong>

                      <p>
                        {reason}
                      </p>
                    </div>
                  </div>
                ),
              )
            ) : (
              <div className="empty-reasons">
                No AI recommendation
                available yet.
              </div>
            )}
          </div>

          <button
            className="analysis-button"
            onClick={() =>
              onNavigate(
                "irrigation",
              )
            }
          >
            View Full Analysis
            <span>→</span>
          </button>
        </article>
      </section>

      <section className="secondary-grid">
        <article className="card chart-card">
          <div className="card-heading">
            <div>
              <span className="heading-icon">
                CH
              </span>

              <h2>
                Irrigation History
              </h2>
            </div>

            <span className="period">
              LIVE
            </span>
          </div>

          <div className="no-history">
            <div className="no-history-icon">
              CH
            </div>

            <h3>
              Live history
            </h3>

            <p>
              Historical recommendations
              will appear here as Nexora
              Agri collects real field
              observations.
            </p>
          </div>
        </article>

        <article className="card field-card">
          <div className="card-heading">
            <div>
              <span className="heading-icon">
                FL
              </span>

              <h2>
                Field Overview
              </h2>
            </div>
          </div>

          <div className="farm-visual">
            <div className="visual-sun" />
            <div className="visual-house" />
            <div className="visual-tree left" />
            <div className="visual-tree right" />
            <div className="crop-stripes one" />
            <div className="crop-stripes two" />
            <div className="crop-stripes three" />
          </div>

          <div className="field-summary">
            <div>
              <span>
                Field
              </span>

              <strong>
                {selectedFieldData?.name ??
                  "--"}
              </strong>
            </div>

            <div>
              <span>
                Area
              </span>

              <strong>
                {selectedFieldData
                  ? `${selectedFieldData.area_hectares} ha`
                  : "--"}
              </strong>
            </div>

            <div>
              <span>
                Soil
              </span>

              <strong>
                {selectedFieldData?.soil_type ??
                  "--"}
              </strong>
            </div>
          </div>

          <button
            className="analysis-button"
            onClick={() =>
              onNavigate("fields")
            }
          >
            View All Fields
            <span>→</span>
          </button>
        </article>

        <article className="card observations-card">
          <div className="card-heading">
            <div>
              <span className="heading-icon">
                OBS
              </span>

              <h2>
                Current Observation
              </h2>
            </div>
          </div>

          <ObservationRow
            title="Soil Moisture"
            value={
              prediction?.soil_moisture !=
              null
                ? `${moisture}%`
                : "--"
            }
            subtitle="Latest real observation"
          />

          <ObservationRow
            title="Rainfall"
            value={
              prediction?.rainfall_mm !=
              null
                ? `${prediction.rainfall_mm} mm`
                : "--"
            }
            subtitle="Latest real observation"
          />

          <ObservationRow
            title="Crop"
            value={
              prediction?.crop ?? "--"
            }
            subtitle="Current analysis"
          />

          <ObservationRow
            title="Urgency"
            value={
              prediction?.urgency ??
              "--"
            }
            subtitle="Decision engine"
          />

          <button
            className="analysis-button"
            onClick={onAddObservation}
          >
            + Record Observation
          </button>
        </article>
      </section>
    </>
  );
}

function ObservationsPage({
  fields,
  observations,
  selectedField,
  onFieldChange,
  onAdd,
}: {
  fields: Field[];
  observations: Observation[];
  selectedField: string;
  onFieldChange: (id: string) => void;
  onAdd: () => void;
}) {
  return (
    <SimplePage
      title="Observations"
      eyebrow="FIELD DATA"
      description="Record real field conditions. These observations feed the Nexora Agri decision engine."
    >
      <div className="page-actions">
        <select
          className="page-select"
          value={selectedField}
          onChange={(event) =>
            onFieldChange(
              event.target.value,
            )
          }
        >
          {fields.map((field) => (
            <option
              key={field.id}
              value={field.id}
            >
              {field.name}
            </option>
          ))}
        </select>

        <button
          className="primary-button"
          onClick={onAdd}
        >
          + Add Observation
        </button>
      </div>

      {observations.length === 0 ? (
        <div className="empty-panel">
          <div className="empty-icon">
            O
          </div>

          <h3>
            No observations recorded
          </h3>

          <p>
            Add the first real observation
            for this field.
          </p>

          <button
            className="primary-button"
            onClick={onAdd}
          >
            Record Observation
          </button>
        </div>
      ) : (
        <div className="observation-table">
          {observations.map(
            (observation) => (
              <div
                className="observation-record"
                key={observation.id}
              >
                <div>
                  <strong>
                    {new Date(
                      observation.observed_at,
                    ).toLocaleString()}
                  </strong>

                  <span>
                    Source:{" "}
                    {observation.source}
                  </span>
                </div>

                <div>
                  <span>
                    Moisture
                  </span>

                  <strong>
                    {observation.soil_moisture ??
                      "--"}
                    %
                  </strong>
                </div>

                <div>
                  <span>
                    Air
                  </span>

                  <strong>
                    {observation.air_temperature ??
                      "--"}
                    °C
                  </strong>
                </div>

                <div>
                  <span>
                    Humidity
                  </span>

                  <strong>
                    {observation.humidity ??
                      "--"}
                    %
                  </strong>
                </div>

                <div>
                  <span>
                    Rainfall
                  </span>

                  <strong>
                    {observation.rainfall_mm ??
                      "--"}{" "}
                    mm
                  </strong>
                </div>
              </div>
            ),
          )}
        </div>
      )}
    </SimplePage>
  );
}

function FieldsPage({
  fields,
  farms,
  selectedField,
  onSelectField,
  onAdd,
  onRefresh,
}: {
  fields: Field[];
  farms: Farm[];
  selectedField: string;
  onSelectField: (id: string) => void;
  onAdd: () => void;
  onRefresh: () => void;
}) {
  return (
    <SimplePage
      title="Fields"
      eyebrow="FIELD MANAGEMENT"
      description="Create and manage real agricultural fields stored in PostgreSQL."
    >
      <div className="page-actions">
        <span>
          {fields.length} registered field
          {fields.length === 1
            ? ""
            : "s"}
        </span>

        <div>
          <button
            className="secondary-button"
            onClick={onRefresh}
          >
            Refresh
          </button>

          <button
            className="primary-button"
            onClick={onAdd}
          >
            + Add Field
          </button>
        </div>
      </div>

      {!fields.length ? (
        <div className="empty-panel">
          <div className="empty-icon">
            F
          </div>

          <h3>
            No fields yet
          </h3>

          <p>
            Create your first real field.
          </p>

          <button
            className="primary-button"
            onClick={onAdd}
          >
            Create First Field
          </button>
        </div>
      ) : (
        <div className="fields-grid">
          {fields.map((field) => (
            <button
              className={`field-tile ${
                selectedField === field.id
                  ? "selected"
                  : ""
              }`}
              key={field.id}
              onClick={() =>
                onSelectField(field.id)
              }
            >
              <div className="field-tile-art">
                F
              </div>

              <div className="field-tile-copy">
                <span className="field-name">
                  {field.name}
                </span>

                <span>
                  {field.area_hectares}{" "}
                  hectares
                </span>

                <span>
                  {field.soil_type ??
                    "Soil type not set"}
                </span>
              </div>

              <span className="tile-arrow">
                →
              </span>
            </button>
          ))}
        </div>
      )}

      <p className="small-note">
        Connected farms: {farms.length}
      </p>
    </SimplePage>
  );
}

function IrrigationPage({
  field,
  prediction,
  confidence,
  irrigation,
  moisture,
  cropStage,
}: {
  field?: Field;
  prediction: Prediction | null;
  confidence: string;
  irrigation: string;
  moisture: string;
  cropStage: string;
}) {
  return (
    <SimplePage
      title="Irrigation Intelligence"
      eyebrow="AI DECISION ENGINE"
      description="Live recommendation generated from the selected field's latest observation."
    >
      <div className="intelligence-grid">
        <div className="card large-analysis">
          <div className="analysis-top">
            <div>
              <span className="detail-label">
                Selected field
              </span>

              <h2>
                {field?.name ??
                  "No field selected"}
              </h2>
            </div>

            <span
              className={`status ${(
                prediction?.predicted_class ??
                ""
              ).toLowerCase()}`}
            >
              {prediction?.predicted_class ??
                "--"}
            </span>
          </div>

          <div className="analysis-number">
            <span>
              Recommended irrigation
            </span>

            <strong>
              {irrigation}
              <small> mm</small>
            </strong>
          </div>

          <div className="recommendation-note">
            {prediction?.action ??
              "No prediction available."}
          </div>

          <DetailRow
            label="Confidence"
            value={confidence}
          />

          <DetailRow
            label="Soil moisture"
            value={`${moisture}%`}
          />

          <DetailRow
            label="Crop stage"
            value={cropStage}
          />
        </div>

        <div className="card probability-card">
          <h2>
            Prediction probabilities
          </h2>

          {prediction ? (
            Object.entries(
              prediction.probabilities,
            ).map(
              ([key, value]) => (
                <div
                  className="probability"
                  key={key}
                >
                  <div>
                    <span>
                      {key}
                    </span>

                    <strong>
                      {(
                        value * 100
                      ).toFixed(1)}
                      %
                    </strong>
                  </div>

                  <div className="bar">
                    <i
                      style={{
                        width: `${value * 100}%`,
                      }}
                    />
                  </div>
                </div>
              ),
            )
          ) : (
            <div className="empty-reasons">
              No prediction loaded.
            </div>
          )}
        </div>
      </div>

      <div className="card reasons-full">
        <h2>
          Decision reasoning
        </h2>

        {prediction?.reasons?.map(
          (reason, index) => (
            <div
              className="reason-line"
              key={index}
            >
              <span>
                {index + 1}
              </span>

              <p>
                {reason}
              </p>
            </div>
          ),
        )}
      </div>
    </SimplePage>
  );
}

function AddObservationModal({
  fields,
  selectedField,
  onClose,
  onCreated,
}: {
  fields: Field[];
  selectedField: string;
  onClose: () => void;
  onCreated: (
    observation: Observation,
  ) => Promise<void>;
}) {
  const [fieldId, setFieldId] =
    useState(selectedField);

  const [observedAt, setObservedAt] =
    useState(
      new Date()
        .toISOString()
        .slice(0, 16),
    );

  const [soilMoisture, setSoilMoisture] =
    useState("");

  const [soilTemperature, setSoilTemperature] =
    useState("");

  const [airTemperature, setAirTemperature] =
    useState("");

  const [humidity, setHumidity] =
    useState("");

  const [rainfall, setRainfall] =
    useState("");

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState("");

  async function submit(
    event: React.FormEvent,
  ) {
    event.preventDefault();

    setError("");
    setSaving(true);

    try {
      const body = {
        field_id: fieldId,
        observed_at: new Date(
          observedAt,
        ).toISOString(),

        soil_moisture:
          soilMoisture === ""
            ? null
            : Number(soilMoisture),

        soil_temperature:
          soilTemperature === ""
            ? null
            : Number(soilTemperature),

        air_temperature:
          airTemperature === ""
            ? null
            : Number(airTemperature),

        humidity:
          humidity === ""
            ? null
            : Number(humidity),

        rainfall_mm:
          rainfall === ""
            ? null
            : Number(rainfall),

        source: "manual",
      };

      const observation =
        await api<Observation>(
          "/api/v1/observations",
          {
            method: "POST",
            body: JSON.stringify(
              body,
            ),
          },
        );

      await onCreated(
        observation,
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to save observation",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <div
      className="modal-backdrop"
      onMouseDown={(event) => {
        if (
          event.target ===
          event.currentTarget
        ) {
          onClose();
        }
      }}
    >
      <form
        className="modal"
        onSubmit={submit}
      >
        <div className="modal-heading">
          <div>
            <span className="eyebrow">
              FIELD OBSERVATION
            </span>

            <h2>
              Add Observation
            </h2>
          </div>

          <button
            type="button"
            className="close-button"
            onClick={onClose}
          >
            X
          </button>
        </div>

        {error && (
          <div className="form-error">
            {error}
          </div>
        )}

        <label>
          Field

          <select
            value={fieldId}
            onChange={(event) =>
              setFieldId(
                event.target.value,
              )
            }
            required
          >
            {fields.map((field) => (
              <option
                key={field.id}
                value={field.id}
              >
                {field.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          Observation date & time

          <input
            type="datetime-local"
            value={observedAt}
            onChange={(event) =>
              setObservedAt(
                event.target.value,
              )
            }
            required
          />
        </label>

        <div className="form-two-column">
          <label>
            Soil moisture (%)

            <input
              type="number"
              min="0"
              max="100"
              step="0.01"
              value={soilMoisture}
              onChange={(event) =>
                setSoilMoisture(
                  event.target.value,
                )
              }
              placeholder="e.g. 31.65"
            />
          </label>

          <label>
            Soil temperature (°C)

            <input
              type="number"
              step="0.1"
              value={soilTemperature}
              onChange={(event) =>
                setSoilTemperature(
                  event.target.value,
                )
              }
              placeholder="e.g. 24.5"
            />
          </label>
        </div>

        <div className="form-two-column">
          <label>
            Air temperature (°C)

            <input
              type="number"
              step="0.1"
              value={airTemperature}
              onChange={(event) =>
                setAirTemperature(
                  event.target.value,
                )
              }
              placeholder="e.g. 29"
            />
          </label>

          <label>
            Humidity (%)

            <input
              type="number"
              min="0"
              max="100"
              step="0.1"
              value={humidity}
              onChange={(event) =>
                setHumidity(
                  event.target.value,
                )
              }
              placeholder="e.g. 62"
            />
          </label>
        </div>

        <label>
          Rainfall (mm)

          <input
            type="number"
            min="0"
            step="0.1"
            value={rainfall}
            onChange={(event) =>
              setRainfall(
                event.target.value,
              )
            }
            placeholder="e.g. 0"
          />
        </label>

        <div className="modal-actions">
          <button
            type="button"
            className="secondary-button"
            onClick={onClose}
          >
            Cancel
          </button>

          <button
            type="submit"
            className="primary-button"
            disabled={saving}
          >
            {saving
              ? "Saving..."
              : "Save Observation"}
          </button>
        </div>
      </form>
    </div>
  );
}

function AddFieldModal({
  farms,
  onClose,
  onCreated,
}: {
  farms: Farm[];
  onClose: () => void;
  onCreated: (
    field: Field,
  ) => Promise<void>;
}) {
  const [farmId, setFarmId] =
    useState(farms[0]?.id ?? "");

  const [name, setName] =
    useState("");

  const [area, setArea] =
    useState("");

  const [soil, setSoil] =
    useState("Loamy");

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState("");

  async function submit(
    event: React.FormEvent,
  ) {
    event.preventDefault();

    setError("");
    setSaving(true);

    try {
      const field =
        await api<Field>(
          "/api/v1/fields",
          {
            method: "POST",
            body: JSON.stringify({
              farm_id: farmId,
              name,
              area_hectares:
                Number(area),
              soil_type:
                soil || null,
            }),
          },
        );

      await onCreated(field);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to create field",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <div
      className="modal-backdrop"
      onMouseDown={(event) => {
        if (
          event.target ===
          event.currentTarget
        ) {
          onClose();
        }
      }}
    >
      <form
        className="modal"
        onSubmit={submit}
      >
        <div className="modal-heading">
          <div>
            <span className="eyebrow">
              NEW FIELD
            </span>

            <h2>
              Add a Field
            </h2>
          </div>

          <button
            type="button"
            className="close-button"
            onClick={onClose}
          >
            X
          </button>
        </div>

        {error && (
          <div className="form-error">
            {error}
          </div>
        )}

        {!farms.length && (
          <div className="form-error">
            No farm exists yet.
            Create a farm before
            adding a field.
          </div>
        )}

        <label>
          Farm

          <select
            value={farmId}
            onChange={(event) =>
              setFarmId(
                event.target.value,
              )
            }
            required
          >
            {farms.map((farm) => (
              <option
                key={farm.id}
                value={farm.id}
              >
                {farm.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          Field name

          <input
            value={name}
            onChange={(event) =>
              setName(
                event.target.value,
              )
            }
            placeholder="e.g. North Tomato Field"
            required
          />
        </label>

        <label>
          Area (hectares)

          <input
            type="number"
            min="0.01"
            step="0.01"
            value={area}
            onChange={(event) =>
              setArea(
                event.target.value,
              )
            }
            placeholder="e.g. 2.5"
            required
          />
        </label>

        <label>
          Soil type

          <input
            value={soil}
            onChange={(event) =>
              setSoil(
                event.target.value,
              )
            }
            placeholder="e.g. Loamy"
          />
        </label>

        <div className="modal-actions">
          <button
            type="button"
            className="secondary-button"
            onClick={onClose}
          >
            Cancel
          </button>

          <button
            type="submit"
            className="primary-button"
            disabled={
              saving || !farms.length
            }
          >
            {saving
              ? "Creating..."
              : "Create Field"}
          </button>
        </div>
      </form>
    </div>
  );
}

function SimplePage({
  title,
  eyebrow,
  description,
  children,
}: {
  title: string;
  eyebrow: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <>
      <section className="page-header">
        <div>
          <div className="eyebrow">
            {eyebrow}
          </div>

          <h1>
            {title}
          </h1>

          <p>
            {description}
          </p>
        </div>
      </section>

      {children}
    </>
  );
}

function MetricCard({
  title,
  value,
  subtitle,
  icon,
  highlight = false,
}: {
  title: string;
  value: string;
  subtitle: string;
  icon: string;
  highlight?: boolean;
}) {
  return (
    <article className="metric-card">
      <div>
        <span className="metric-title">
          {title}
        </span>

        <strong
          className={
            highlight
              ? "green-value"
              : ""
          }
        >
          {value}
        </strong>

        <span className="metric-subtitle">
          {subtitle}
        </span>
      </div>

      <div className="metric-art">
        {icon}
      </div>
    </article>
  );
}

function DetailRow({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="detail-row">
      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>
    </div>
  );
}

function ObservationRow({
  title,
  subtitle,
  value,
}: {
  title: string;
  subtitle: string;
  value: string;
}) {
  return (
    <div className="observation">
      <div className="observation-icon">
        {title.slice(0, 1)}
      </div>

      <div className="observation-copy">
        <strong>
          {title}
        </strong>

        <span>
          {subtitle}
        </span>
      </div>

      <strong className="observation-value">
        {value}
      </strong>
    </div>
  );
}

function Gauge({
  prediction,
  predictionClass,
}: {
  prediction: Prediction | null;
  predictionClass: string;
}) {
  const progress = prediction
    ? Math.max(
        8,
        Math.min(
          72,
          prediction.confidence * 72,
        ),
      )
    : 0;

  return (
    <div className="gauge-wrap">
      <div
        className="gauge"
        style={
          {
            "--progress": `${progress}%`,
          } as React.CSSProperties
        }
      >
        <div className="gauge-inner">
          <strong>
            {predictionClass}
          </strong>

          <span>
            Irrigation Level
          </span>
        </div>
      </div>
    </div>
  );
}

export default App;
