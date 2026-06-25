import workspaceSnapshot from "../../../tests/fixtures/synthetic_ui_map_workspace/map-workspace-response-v1.json";

export type MapPin = {
  id: string;
  display_label: string;
  latitude: number;
  longitude: number;
  property_type: string;
  record_type: string;
  stale_flag: boolean;
  status: string;
  verification_status: string;
};

export type TableRow = MapPin & {
  address: string;
  city: string;
  confidence_summary: string;
  evidence_link_count: number;
  passport_id: string | null;
  state: string;
};

export type MapWorkspaceSnapshot = {
  available_filters: Record<string, Array<string | boolean>>;
  map_pins: Array<MapPin & { is_selected: boolean }>;
  result_counts: {
    filtered_records: number;
    map_pins: number;
    stale_records: number;
    total_records: number;
    by_record_type: Record<string, number>;
  };
  schema_version: string;
  selected_record: TableRow | null;
  table_rows: Array<TableRow & { is_selected: boolean }>;
};

export const mapWorkspaceData = workspaceSnapshot as MapWorkspaceSnapshot;

export function getInitialSelectedId(snapshot: MapWorkspaceSnapshot = mapWorkspaceData) {
  return (
    snapshot.selected_record?.id ??
    snapshot.table_rows.find((row) => row.is_selected)?.id ??
    snapshot.table_rows[0]?.id ??
    ""
  );
}

export function findSelectedRow(selectedId: string, snapshot: MapWorkspaceSnapshot = mapWorkspaceData) {
  return snapshot.table_rows.find((row) => row.id === selectedId) ?? snapshot.table_rows[0];
}

export function formatLabel(value: string) {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function coordinatePlanePosition(pin: MapPin, pins: MapPin[]) {
  const latitudes = pins.map((item) => item.latitude);
  const longitudes = pins.map((item) => item.longitude);
  const minLatitude = Math.min(...latitudes);
  const maxLatitude = Math.max(...latitudes);
  const minLongitude = Math.min(...longitudes);
  const maxLongitude = Math.max(...longitudes);
  const latitudeRange = maxLatitude - minLatitude || 1;
  const longitudeRange = maxLongitude - minLongitude || 1;

  return {
    left: `${8 + ((pin.longitude - minLongitude) / longitudeRange) * 84}%`,
    top: `${8 + (1 - (pin.latitude - minLatitude) / latitudeRange) * 84}%`
  };
}
