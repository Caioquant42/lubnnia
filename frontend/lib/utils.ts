/**
 * Utility functions for the application
 * This file contains helper functions used throughout the codebase
 */

import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * Combines multiple class names into a single string, merging Tailwind CSS classes intelligently
 * Uses clsx for conditional class names and tailwind-merge to prevent class conflicts
 * 
 * @param inputs - Class names to combine (can be strings, objects, arrays, etc.)
 * @returns A single string with all classes merged properly
 * 
 * @example
 * cn("px-2 py-1", "px-4") // returns "py-1 px-4" (px-4 overrides px-2)
 * cn("text-red-500", isActive && "text-blue-500") // conditional classes
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format a number with specified decimal places and locale formatting
 * Handles undefined and NaN values gracefully
 * 
 * @param value - The number to format
 * @param decimals - Number of decimal places (default: 2)
 * @returns Formatted string or "-" if value is invalid
 * 
 * @example
 * formatNumber(1234.5678, 2) // returns "1.234,57" (pt-BR locale)
 * formatNumber(undefined) // returns "-"
 */
export function formatNumber(value: number | undefined, decimals: number = 2): string {
  if (value === undefined || isNaN(value)) return "-";
  return value.toLocaleString('pt-BR', {
    style: 'decimal',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/**
 * Format a value as percentage
 * 
 * @param value - The number to format as percentage
 * @returns Formatted percentage string
 * 
 * @example
 * formatPercentage(0.1534) // returns "15,3%"
 * formatPercentage(undefined) // returns "-"
 */
export function formatPercentage(value: number | undefined): string {
  if (value === undefined || isNaN(value)) return "-";
  return `${(value * 100).toLocaleString('pt-BR', {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  })}%`;
}

/**
 * Format currency in BRL (Brazilian Real)
 * 
 * @param value - The number to format as currency
 * @returns Formatted currency string
 * 
 * @example
 * formatCurrency(1234.56) // returns "R$ 1.234,56"
 * formatCurrency(undefined) // returns "-"
 */
export function formatCurrency(value: number | undefined): string {
  if (value === undefined || isNaN(value)) return "-";
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value);
}

