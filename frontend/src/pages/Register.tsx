import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { z } from 'zod'
import { useAuth } from '@/contexts/AuthContext'
import { Form, FormInput } from '@/components/form'
import { Button, Alert } from '@/components/ui'
import { Building2 } from 'lucide-react'

const registerSchema = z.object({
  companyName: z.string().min(2, 'Company name must be at least 2 characters'),
  companyEmail: z.string().email('Please enter a valid company email'),
  firstName: z.string().min(2, 'First name must be at least 2 characters'),
  lastName: z.string().min(2, 'Last name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email address'),
  phone: z.string().optional(),
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

type RegisterFormData = z.infer<typeof registerSchema>

export function Register() {
  const navigate = useNavigate()
  const { register } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string>('')

  const handleSubmit = async (data: RegisterFormData) => {
    setIsLoading(true)
    setError('')

    try {
      const { confirmPassword, ...registerData } = data
      await register(registerData)
      navigate('/dashboard', { replace: true })
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Registration failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl w-full space-y-8">
        {/* Logo and Header */}
        <div className="text-center">
          <div className="flex justify-center">
            <div className="bg-primary-100 dark:bg-primary-900/20 p-3 rounded-xl">
              <Building2 className="h-12 w-12 text-primary-600 dark:text-primary-400" />
            </div>
          </div>
          <h2 className="mt-6 text-3xl font-bold text-gray-900 dark:text-white">
            Start your free trial
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Create your BuiltEnvironment.ai account and get started in minutes
          </p>
        </div>

        {/* Registration Form */}
        <div className="bg-white dark:bg-gray-800 py-8 px-4 shadow-lg rounded-lg sm:px-10 border border-gray-200 dark:border-gray-700">
          {error && (
            <Alert variant="danger" className="mb-6">
              {error}
            </Alert>
          )}

          <Form<RegisterFormData>
            onSubmit={handleSubmit}
            schema={registerSchema}
            defaultValues={{
              companyName: '',
              companyEmail: '',
              firstName: '',
              lastName: '',
              email: '',
              phone: '',
              password: '',
              confirmPassword: '',
            }}
          >
            {({ control, formState: { isValid } }) => (
              <div className="space-y-6">
                {/* Company Information */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Company Information
                  </h3>
                  <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div className="sm:col-span-2">
                      <FormInput
                        name="companyName"
                        control={control}
                        label="Company Name"
                        placeholder="Acme Construction Ltd"
                        disabled={isLoading}
                      />
                    </div>
                    <div className="sm:col-span-2">
                      <FormInput
                        name="companyEmail"
                        control={control}
                        label="Company Email"
                        type="email"
                        placeholder="contact@company.com"
                        disabled={isLoading}
                      />
                    </div>
                  </div>
                </div>

                {/* Personal Information */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Your Information
                  </h3>
                  <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <FormInput
                      name="firstName"
                      control={control}
                      label="First Name"
                      placeholder="John"
                      disabled={isLoading}
                    />
                    <FormInput
                      name="lastName"
                      control={control}
                      label="Last Name"
                      placeholder="Smith"
                      disabled={isLoading}
                    />
                    <div className="sm:col-span-2">
                      <FormInput
                        name="email"
                        control={control}
                        label="Email Address"
                        type="email"
                        placeholder="john@company.com"
                        autoComplete="email"
                        disabled={isLoading}
                      />
                    </div>
                    <div className="sm:col-span-2">
                      <FormInput
                        name="phone"
                        control={control}
                        label="Phone Number (Optional)"
                        type="tel"
                        placeholder="+44 20 1234 5678"
                        disabled={isLoading}
                      />
                    </div>
                  </div>
                </div>

                {/* Password */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Create Password
                  </h3>
                  <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div className="sm:col-span-2">
                      <FormInput
                        name="password"
                        control={control}
                        label="Password"
                        type="password"
                        placeholder="Create a strong password"
                        autoComplete="new-password"
                        helperText="At least 8 characters with uppercase, lowercase, and number"
                        disabled={isLoading}
                      />
                    </div>
                    <div className="sm:col-span-2">
                      <FormInput
                        name="confirmPassword"
                        control={control}
                        label="Confirm Password"
                        type="password"
                        placeholder="Confirm your password"
                        autoComplete="new-password"
                        disabled={isLoading}
                      />
                    </div>
                  </div>
                </div>

                <div className="pt-4">
                  <Button
                    type="submit"
                    variant="primary"
                    fullWidth
                    isLoading={isLoading}
                    disabled={!isValid || isLoading}
                  >
                    Create account
                  </Button>
                </div>

                <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
                  By creating an account, you agree to our Terms of Service and Privacy Policy
                </p>
              </div>
            )}
          </Form>
        </div>

        {/* Sign in link */}
        <p className="text-center text-sm text-gray-600 dark:text-gray-400">
          Already have an account?{' '}
          <Link
            to="/login"
            className="font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300"
          >
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
