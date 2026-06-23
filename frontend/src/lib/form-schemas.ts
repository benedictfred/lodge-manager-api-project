import { z } from "zod";

export const loginSchema = z.object({
  email: z
    .email("Please enter a valid email address")
    .min(1, "Email is required"),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .max(20, "Password is too long"),
});

export type LoginFormData = z.infer<typeof loginSchema>;

export const landlordSignUpSchema = z.object({
  first_name: z.string().min(1, "First name is required"),
  last_name: z.string().min(1, "Last name is required"),
  email: z
    .email("Please enter a valid email address")
    .min(1, "Email is required"),
  phone_no: z
    .string()
    .min(1, "Phone number is required")
    .max(15, "Phone number is too long"),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .max(128, "Password is too long"),
});

export const tenantSignUpSchema = z.object({
  first_name: z.string().min(1, "First name is required"),
  last_name: z.string().min(1, "Last name is required"),
  email: z
    .email("Please enter a valid email address")
    .min(1, "Email is required"),
  phone_no: z
    .string()
    .min(1, "Phone number is required")
    .max(15, "Phone number is too long"),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .max(128, "Password is too long"),
  lodge_id: z.coerce.number().min(1, "Lodge ID is required"),
  tenant_type: z.enum(["Student", "Others"]),
  emergency_contact_name: z
    .string()
    .min(1, "Emergency contact name is required"),
  emergency_contact_phone_no: z
    .string()
    .min(1, "Emergency contact phone is required")
    .max(15, "Phone number is too long"),
  level: z
    .enum(["100", "200", "300", "400", "500", "600"])
    .optional()
    .or(z.literal("")),
  reg_no: z.coerce
    .number()
    .optional()
    .or(z.literal("").transform(() => undefined)),
  department: z.string().optional(),
});

export type LandlordSignUpFormData = z.infer<typeof landlordSignUpSchema>;
export type TenantSignUpFormData = z.infer<typeof tenantSignUpSchema>;
