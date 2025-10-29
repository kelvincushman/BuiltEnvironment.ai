import React from 'react'
import { useForm, UseFormReturn, FieldValues, SubmitHandler } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z, ZodSchema } from 'zod'

export interface FormProps<T extends FieldValues> {
  onSubmit: SubmitHandler<T>
  schema?: ZodSchema<T>
  defaultValues?: Partial<T>
  children: (methods: UseFormReturn<T>) => React.ReactNode
  className?: string
}

export function Form<T extends FieldValues>({
  onSubmit,
  schema,
  defaultValues,
  children,
  className,
}: FormProps<T>) {
  const methods = useForm<T>({
    resolver: schema ? zodResolver(schema) : undefined,
    defaultValues,
  })

  return (
    <form onSubmit={methods.handleSubmit(onSubmit)} className={className} noValidate>
      {children(methods)}
    </form>
  )
}
