import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { z } from 'zod'
import { Form, FormInput } from '@/components/form'
import { Button, Alert } from '@/components/ui'
import { Building2, Mail, ArrowLeft } from 'lucide-react'
import { authService } from '@/services/auth'

const forgotPasswordSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
})

type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>

export function ForgotPassword() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string>('')
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (data: ForgotPasswordFormData) => {
    setIsLoading(true)
    setError('')
    setSuccess(false)

    try {
      await authService.forgotPassword(data.email)
      setSuccess(true)
    } catch (err: any) {
      setError(
        err.response?.data?.error?.message ||
        'Failed to send reset email. Please try again.'
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
            Reset your password
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Enter your email and we'll send you a link to reset your password
          </p>
        </div>

        {/* Forgot Password Form */}
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
                  <Mail className="h-8 w-8 text-success-600 dark:text-success-400" />
                </div>
              </div>
              <Alert variant="success">
                Check your email! We've sent you instructions to reset your password.
              </Alert>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Didn't receive the email? Check your spam folder or try again.
              </p>
              <Button
                variant="outline"
                fullWidth
                onClick={() => setSuccess(false)}
              >
                Try another email
              </Button>
            </div>
          ) : (
            <Form<ForgotPasswordFormData>
              onSubmit={handleSubmit}
              schema={forgotPasswordSchema}
              defaultValues={{ email: '' }}
            >
              {({ control, formState: { isValid } }) => (
                <div className="space-y-6">
                  <FormInput
                    name="email"
                    control={control}
                    label="Email address"
                    type="email"
                    placeholder="you@company.com"
                    autoComplete="email"
                    disabled={isLoading}
                  />

                  <Button
                    type="submit"
                    variant="primary"
                    fullWidth
                    isLoading={isLoading}
                    disabled={!isValid || isLoading}
                  >
                    Send reset link
                  </Button>
                </div>
              )}
            </Form>
          )}
        </div>

        {/* Back to login link */}
        <div className="text-center">
          <Link
            to="/login"
            className="inline-flex items-center text-sm font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to login
          </Link>
        </div>
      </div>
    </div>
  )
}
