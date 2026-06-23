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
import { landlordSignUpSchema, type LandlordSignUpFormData } from "../../lib/form-schemas";
import { useLandlordSignUp } from "../../hooks/auth";

export function LandlordSignUpForm() {
  const { mutate, isPending } = useLandlordSignUp();

  const form = useForm<LandlordSignUpFormData>({
    resolver: zodResolver(landlordSignUpSchema),
    defaultValues: {
      first_name: "",
      last_name: "",
      email: "",
      phone_no: "",
      password: "",
    },
  });

  const onSubmit = (data: LandlordSignUpFormData) => {
    mutate(data);
  };

  return (
    <Form form={form} onSubmit={form.handleSubmit(onSubmit)}>
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <FormField
            name="first_name"
            render={({ field, fieldState }) => (
              <FormItem>
                <FormLabel>First Name</FormLabel>
                <FormControl>
                  <Input {...field} placeholder="John" />
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
        
        <FormField
          name="email"
          render={({ field, fieldState }) => (
            <FormItem>
              <FormLabel>Email Address</FormLabel>
              <FormControl>
                <Input {...field} type="email" placeholder="john@example.com" />
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

        <Button
          type="submit"
          className="w-full mt-6"
          isLoading={isPending}
          disabled={isPending}
        >
          Sign Up as Landlord
        </Button>
      </div>
    </Form>
  );
}
