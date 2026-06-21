import { axiosInstance } from "../lib/axios";
import {
  type LoginFormData,
  type LandlordSignUpFormData,
  type TenantSignUpFormData,
} from "../lib/form-schemas";
import { type LoginResponse } from "../types/auth";

export const login = async (data: LoginFormData): Promise<LoginResponse> => {
  const formData = new FormData();
  formData.append("username", data.email);
  formData.append("password", data.password);

  const response = await axiosInstance.post<LoginResponse>(
    "/auth/login",
    formData,
  );
  return response.data;
};

export const registerLandlord = async (data: LandlordSignUpFormData) => {
  const response = await axiosInstance.post("/auth/register/landlord", data);
  return response.data;
};

export const registerTenant = async (data: TenantSignUpFormData) => {
  const payload = {
    user_info: {
      first_name: data.first_name,
      last_name: data.last_name,
      email: data.email,
      phone_no: data.phone_no,
      password: data.password,
    },
    tenant_info: {
      lodge_id: data.lodge_id,
      tenant_type: data.tenant_type,
      emergency_contact_name: data.emergency_contact_name,
      emergency_contact_phone_no: data.emergency_contact_phone_no,
      level: data.level || null,
      reg_no: data.reg_no || null,
      department: data.department || null,
    },
  };
  const response = await axiosInstance.post("/auth/register/tenant", payload);
  return response.data;
};
