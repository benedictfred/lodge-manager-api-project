import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormMessage,
} from "../ui/form";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import { tenantSignUpSchema, type TenantSignUpFormData } from "../../lib/form-schemas";
import { useTenantSignUp } from "../../hooks/auth";

export function TenantSignUpForm() {
  const { mutate, isPending } = useTenantSignUp();

  const form = useForm<TenantSignUpFormData>({
    resolver: zodResolver(tenantSignUpSchema),
    defaultValues: {
      first_name: "",
      last_name: "",
      email: "",
      phone_no: "",
      password: "",
      lodge_id: "" as any,
      tenant_type: "Student",
      emergency_contact_name: "",
      emergency_contact_phone_no: "",
      level: "",
      reg_no: "" as any,
      department: "",
    },
  });

  const onSubmit = (data: TenantSignUpFormData) => {
    mutate(data);
  };

  const tenantType = form.watch("tenant_type");

  return (
    <Form form={form} onSubmit={form.handleSubmit(onSubmit)}>
      <div className="space-y-4">
        {/* Personal Details */}
        <div className="grid grid-cols-2 gap-4">
          <FormField
            name="first_name"
            render={({ field, fieldState }) => (
              <FormItem>
                <FormLabel>First Name</FormLabel>
                <FormControl>
                  <Input {...field} placeholder="Jane" />
                </FormControl>
                <FormMessage error={fieldState.error?.message} />
              </FormItem>
            )}
          />
          <FormField
            name="last_name"
            render={({ field, fieldState }) => (
              <FormItem>
                <FormLabel>Last Name</FormLabel>
                <FormControl>
                  <Input {...field} placeholder="Doe" />
                </FormControl>
                <FormMessage error={fieldState.error?.message} />
              </FormItem>
            )}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <FormField
            name="email"
            render={({ field, fieldState }) => (
              <FormItem>
                <FormLabel>Email Address</FormLabel>
                <FormControl>
                  <Input {...field} type="email" placeholder="jane@example.com" />
                </FormControl>
                <FormMessage error={fieldState.error?.message} />
              </FormItem>
            )}
          />
          <FormField
            name="phone_no"
            render={({ field, fieldState }) => (
              <FormItem>
                <FormLabel>Phone Number</FormLabel>
                <FormControl>
                  <Input {...field} type="tel" placeholder="+1234567890" />
                </FormControl>
                <FormMessage error={fieldState.error?.message} />
              </FormItem>
            )}
          />
        </div>

        <FormField
          name="password"
          render={({ field, fieldState }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <Input {...field} type="password" placeholder="••••••••" />
              </FormControl>
              <FormMessage error={fieldState.error?.message} />
            </FormItem>
          )}
        />

        {/* Tenant Details */}
        <div className="grid grid-cols-2 gap-4">
          <FormField
            name="lodge_id"
            render={({ field, fieldState }) => (
              <FormItem>
                <FormLabel>Lodge ID</FormLabel>
                <FormControl>
                  <Input {...field} type="number" placeholder="1" />
                </FormControl>
                <FormMessage error={fieldState.error?.message} />
              </FormItem>
            )}
          />
          <FormField
            name="tenant_type"
            render={({ field, fieldState }) => (
              <FormItem>
                <FormLabel>Tenant Type</FormLabel>
                <FormControl>
                  <select
                    {...field}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <option value="Student">Student</option>
                    <option value="Others">Others</option>
                  </select>
                </FormControl>
                <FormMessage error={fieldState.error?.message} />
              </FormItem>
            )}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <FormField
            name="emergency_contact_name"
            render={({ field, fieldState }) => (
              <FormItem>
                <FormLabel>Emergency Contact</FormLabel>
                <FormControl>
                  <Input {...field} placeholder="Contact Name" />
                </FormControl>
                <FormMessage error={fieldState.error?.message} />
              </FormItem>
            )}
          />
          <FormField
            name="emergency_contact_phone_no"
            render={({ field, fieldState }) => (
              <FormItem>
                <FormLabel>Emergency Phone</FormLabel>
                <FormControl>
                  <Input {...field} placeholder="+1234567890" />
                </FormControl>
                <FormMessage error={fieldState.error?.message} />
              </FormItem>
            )}
          />
        </div>

        {tenantType === "Student" && (
          <>
            <div className="grid grid-cols-2 gap-4">
              <FormField
                name="level"
                render={({ field, fieldState }) => (
                  <FormItem>
                    <FormLabel>Level</FormLabel>
                    <FormControl>
                      <select
                        {...field}
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        <option value="">Select Level...</option>
                        <option value="100">100</option>
                        <option value="200">200</option>
                        <option value="300">300</option>
                        <option value="400">400</option>
                        <option value="500">500</option>
                        <option value="600">600</option>
                      </select>
                    </FormControl>
                    <FormMessage error={fieldState.error?.message} />
                  </FormItem>
                )}
              />
              <FormField
                name="reg_no"
                render={({ field, fieldState }) => (
                  <FormItem>
                    <FormLabel>Registration Number</FormLabel>
                    <FormControl>
                      <Input {...field} type="number" placeholder="Reg Number" value={field.value || ""} />
                    </FormControl>
                    <FormMessage error={fieldState.error?.message} />
                  </FormItem>
                )}
              />
            </div>
            <FormField
              name="department"
              render={({ field, fieldState }) => (
                <FormItem>
                  <FormLabel>Department</FormLabel>
                  <FormControl>
                    <Input {...field} placeholder="Computer Science" />
                  </FormControl>
                  <FormMessage error={fieldState.error?.message} />
                </FormItem>
              )}
            />
          </>
        )}

        <Button
          type="submit"
          className="w-full mt-6"
          isLoading={isPending}
          disabled={isPending}
        >
          Sign Up as Tenant
        </Button>
      </div>
    </Form>
  );
}
