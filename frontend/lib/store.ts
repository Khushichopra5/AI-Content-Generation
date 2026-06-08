"use client";

import { create } from "zustand";

import type { GuestBootstrapResponse } from "@/lib/types";

type InspectorEntry = {
  label: string;
  payload: unknown;
};

type AppState = {
  guest: GuestBootstrapResponse | null;
  lastRequest: InspectorEntry | null;
  lastResponse: InspectorEntry | null;
  setGuest: (guest: GuestBootstrapResponse) => void;
  setLastRequest: (entry: InspectorEntry | null) => void;
  setLastResponse: (entry: InspectorEntry | null) => void;
};

export const useAppStore = create<AppState>((set) => ({
  guest: null,
  lastRequest: null,
  lastResponse: null,
  setGuest: (guest) => set({ guest }),
  setLastRequest: (lastRequest) => set({ lastRequest }),
  setLastResponse: (lastResponse) => set({ lastResponse })
}));
