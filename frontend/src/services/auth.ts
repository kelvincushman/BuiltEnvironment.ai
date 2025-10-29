import { api } from './api'

interface LoginResponse {
  accessToken: string
  refreshToken: string
  tokenType: string
}

interface RegisterRequest {
  companyName: string
  companyEmail: string
  firstName: string
  lastName: string
  email: string
  password: string
  phone?: string
}

interface User {
  id: string
  tenantId: string
  email: string
  firstName: string
  lastName: string
  phone: string | null
  jobTitle: string | null
  isActive: boolean
  isVerified: boolean
  isEngineer: boolean
  engineerRegistrationNumber: string | null
  engineerQualification: string | null
  role: string
  createdAt: string
  lastLoginAt: string | null
}

export const authService = {
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/auth/login', {
      email,
      password,
    })
    return response.data
  },

  async register(data: RegisterRequest): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/auth/register', data)
    return response.data
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/users/me')
    return response.data
  },

  async updateProfile(data: {
    firstName?: string
    lastName?: string
    phone?: string
    jobTitle?: string
  }): Promise<User> {
    const response = await api.patch<User>('/users/me', data)
    return response.data
  },

  async changePassword(currentPassword: string, newPassword: string): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>('/users/me/change-password', {
      currentPassword,
      newPassword,
    })
    return response.data
  },

  async forgotPassword(email: string): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>('/auth/forgot-password', {
      email,
    })
    return response.data
  },

  async resetPassword(token: string, newPassword: string): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>('/auth/reset-password', {
      token,
      newPassword,
    })
    return response.data
  },
}
