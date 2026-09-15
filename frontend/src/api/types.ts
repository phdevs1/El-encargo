export type WaitlistStatus = "waiting" | "called" | "seated" | "cancelled" | "no_show";

export interface LocationSummaryResponse {
  name: string;
  slug: string;
  country: string;
}

export interface JoinWaitlistRequest {
  name: string;
  phone: string;
  party_size: number;
}

export interface JoinWaitlistResponse {
  public_token: string;
  position: number;
  estimated_wait_minutes: number;
  status: WaitlistStatus;
  location_id: number;
}

export interface WaitlistEntryStatusResponse {
  public_token: string;
  status: WaitlistStatus;
  position: number | null;
  estimated_wait_minutes: number | null;
  party_size: number;
  guest_name: string;
}

export interface HostQueueEntryResponse {
  id: number;
  public_token: string;
  guest_name: string;
  phone_e164: string;
  party_size: number;
  status: WaitlistStatus;
  position: number;
  is_frequent_guest: boolean;
  joined_at: string;
  called_at: string | null;
  estimated_wait_minutes_at_join: number | null;
  version: number;
}

export interface HostQueueListResponse {
  entries: HostQueueEntryResponse[];
}

export interface ReorderRequest {
  after_entry_id: number | null;
}

export interface WaitlistEntryActionResponse {
  id: number;
  status: WaitlistStatus;
  version: number;
  called_at: string | null;
  seated_at: string | null;
  cancelled_at: string | null;
  no_show_at: string | null;
  sort_order: string | null;
  location_id: number;
}

/** Message pushed over the host queue WebSocket — same shape as the REST list response. */
export type QueueUpdateMessage = HostQueueListResponse;
