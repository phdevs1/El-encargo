import { apiGet, apiPatch, apiPost } from "./client";
import type {
  HostQueueListResponse,
  JoinWaitlistRequest,
  JoinWaitlistResponse,
  LocationSummaryResponse,
  WaitlistEntryActionResponse,
  WaitlistEntryStatusResponse,
} from "./types";

export const getLocationSummary = (slug: string) =>
  apiGet<LocationSummaryResponse>(`/locations/${slug}`);

export const joinWaitlist = (slug: string, body: JoinWaitlistRequest) =>
  apiPost<JoinWaitlistResponse>(`/locations/${slug}/waitlist-entries`, body);

export const getEntryStatus = (token: string) =>
  apiGet<WaitlistEntryStatusResponse>(`/waitlist-entries/${token}`);

export const cancelEntry = (token: string) =>
  apiPost<WaitlistEntryActionResponse>(`/waitlist-entries/${token}/cancel`);

export const listHostQueue = (locationId: number) =>
  apiGet<HostQueueListResponse>(`/locations/${locationId}/waitlist-entries`);

export const callEntry = (entryId: number) =>
  apiPost<WaitlistEntryActionResponse>(`/waitlist-entries/${entryId}/call`);

export const seatEntry = (entryId: number) =>
  apiPost<WaitlistEntryActionResponse>(`/waitlist-entries/${entryId}/seat`);

export const markNoShow = (entryId: number) =>
  apiPost<WaitlistEntryActionResponse>(`/waitlist-entries/${entryId}/no-show`);

export const reorderEntry = (entryId: number, afterEntryId: number | null) =>
  apiPatch<WaitlistEntryActionResponse>(`/waitlist-entries/${entryId}/reorder`, {
    after_entry_id: afterEntryId,
  });
