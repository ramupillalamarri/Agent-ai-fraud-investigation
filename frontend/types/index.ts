import type * as React from "react";

/** Base entity fields shared across domain models. */
export interface BaseEntity {
  id: string;
  createdAt: string;
  updatedAt: string;
}

/** Navigation item for sidebar / top-nav. */
export interface NavItem {
  title: string;
  href: string;
  icon?: React.ElementType;
  badge?: string | number;
  disabled?: boolean;
  external?: boolean;
  children?: NavItem[];
}

/** Sidebar navigation group. */
export interface NavGroup {
  label?: string;
  items: NavItem[];
}

/** Generic API response envelope. */
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

/** Paginated response wrapper. */
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

/** Severity levels for fraud signals. */
export type Severity = "critical" | "high" | "medium" | "low" | "info";

/** Status of a fraud investigation case. */
export type CaseStatus = "open" | "in_review" | "escalated" | "resolved" | "closed";

/** User role within the platform. */
export type UserRole = "admin" | "investigator" | "analyst" | "viewer";
