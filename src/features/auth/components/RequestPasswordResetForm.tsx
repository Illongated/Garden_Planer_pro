import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import LoadingSpinner from '@/components/loading-spinner';
import { toast } from 'sonner';
import { requestPasswordResetSchema, RequestPasswordResetSchema } from '../schemas';
import api from '@/lib/api';

export const RequestPasswordResetForm = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RequestPasswordResetSchema>({
    resolver: zodResolver(requestPasswordResetSchema),
  });

  const onSubmit = async (data: RequestPasswordResetSchema) => {
    setIsLoading(true);
    try {
      await api.post('/auth/request-password-reset', { email: data.email });
      setIsSubmitted(true);
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'An unknown error occurred.';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  if (isSubmitted) {
    return (
      <div className="text-center">
        <h3 className="text-lg font-semibold">Check Your Email</h3>
        <p className="text-muted-foreground mt-2">
          If an account with that email exists, we have sent a password reset link to it.
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          placeholder="m@example.com"
          {...register('email')}
        />
        {errors.email && <p className="text-sm text-destructive">{errors.email.message}</p>}
      </div>
      <Button type="submit" className="w-full" disabled={isLoading}>
        {isLoading && <LoadingSpinner className="mr-2 h-4 w-4" />}
        Send Reset Link
      </Button>
    </form>
  );
};
