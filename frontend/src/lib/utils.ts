import { isAxiosError } from "axios";
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const processErrorMessage = (
  error: unknown,
  fallbackMsg = "Network Error",
) => {
  if (isAxiosError(error)) {
    return error.response?.data?.message ?? error.message ?? fallbackMsg;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return fallbackMsg;
};
