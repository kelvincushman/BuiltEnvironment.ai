import React, { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { z } from 'zod'
import { Form, FormInput } from '@/components/form'
import { Button, Alert } from '@/components/ui'
import { Building2, CheckCircle } from 'lucide-react'
import { authService } from '@/services/auth'

const resetPasswordSchema = z.object({
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
})

type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>

export function ResetPassword() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')

  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string>('')
  const [success, setSuccess] = useState(false)

  // Check if token is present
  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <div className="flex justify-center">
              <div className="bg-primary-100 dark:bg-primary-900/20 p-3 rounded-xl">
                <Building2 className="h-12 w-12 text-primary-600 dark:text-primary-400" />
              </div>
            </div>
            <h2 className="mt-6 text-3xl font-bold text-gray-900 dark:text-white">
              Invalid reset link
            </h2>
          </div>
          <div className="bg-white dark:bg-gray-800 py-8 px-4 shadow-lg rounded-lg sm:px-10 border border-gray-200 dark:border-gray-700">
            <Alert variant="danger" className="mb-6">
              This password reset link is invalid or has expired. Please request a new one.
            </Alert>
            <Link to="/forgot-password">
              <Button variant="primary" fullWidth>
                Request new reset link
              </Button>
            </Link>
          </div>
        </div>
      </div>
    )
  }

  const handleSubmit = async (data: ResetPasswordFormData) => {
    setIsLoading(true)
    setError('')
    setSuccess(false)

    try {
      await authService.resetPassword(token, data.password)
      setSuccess(true)
      // Redirect to login after 3 seconds
      setTimeout(() => {
        navigate('/login', { replace: true })
      }, 3000)
    } catch (err: any) {
      setError(
        err.response?.data?.error?.message ||
        'Failed to reset password. The link may be invalid or expired.'
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Logo and Header */}
        <div className="text-center">
          <div className="flex justify-center">
            <div className="bg-primary-100 dark:bg-primary-900/20 p-3 rounded-xl">
              <Building2 className="h-12 w-12 text-primary-600 dark:text-primary-400" />
            </div>
          </div>
          <h2 className="mt-6 text-3xl font-bold text-gray-900 dark:text-white">
            Set new password
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Create a strong password for your account
          </p>
        </div>

        {/* Reset Password Form */}
        <div className="bg-white dark:bg-gray-800 py-8 px-4 shadow-lg rounded-lg sm:px-10 border border-gray-200 dark:border-gray-700">
          {error && (
            <Alert variant="danger" className="mb-6">
              {error}
            </Alert>
          )}

          {success ? (
            <div className="text-center space-y-4">
              <div className="flex justify-center">
                <div className="bg-success-100 dark:bg-success-900/20 p-3 rounded-full">
                  <CheckCircle className="h-8 w-8 text-success-600 dark:text-success-400" />
                </div>
              </div>
              <Alert variant="success">
                Password reset successfully! Redirecting to login...
              </Alert>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                You can now sign in with your new password.
              </p>
            </div>
          ) : (
            <Form<ResetPasswordFormData>
              onSubmit={handleSubmit}
              schema={resetPasswordSchema}
              defaultValues={{ password: '', confirmPassword: '' }}
            >
              {({ control, formState: { isValid } }) => (
                <div className="space-y-6">
                  <FormInput
                    name="password"
                    control={control}
                    label="New Password"
                    type="password"
                    placeholder="Create a strong password"
                    autoComplete="new-password"
                    helperText="At least 8 characters with uppercase, lowercase, and number"
                    disabled={isLoading}
                  />

                  <FormInput
                    name="confirmPassword"
                    control={control}
                    label="Confirm Password"
                    type="password"
                    placeholder="Confirm your password"
                    autoComplete="new-password"
                    disabled={isLoading}
                  />

                  <Button
                    type="submit"
                    variant="primary"
                    fullWidth
                    isLoading={isLoading}
                    disabled={!isValid || isLoading}
                  >
                    Reset password
                  </Button>
                </div>
              )}
            </Form>
          )}
        </div>

        {/* Back to login link */}
        {!success && (
          <p className="text-center text-sm text-gray-600 dark:text-gray-400">
            Remember your password?{' '}
            <Link
              to="/login"
              className="font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300"
            >
              Sign in
            </Link>
          </p>
        )}
      </div>
    </div>
  )
}
