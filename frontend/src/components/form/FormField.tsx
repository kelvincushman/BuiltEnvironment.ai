import React from 'react'
import { useController, UseControllerProps, FieldValues } from 'react-hook-form'
import { Input, InputProps } from '../ui/Input'
import { Select, SelectProps } from '../ui/Select'
import { Textarea, TextareaProps } from '../ui/Textarea'

// FormInput - integrates Input with react-hook-form
export interface FormInputProps<T extends FieldValues>
  extends Omit<InputProps, 'name'>,
    UseControllerProps<T> {}

export function FormInput<T extends FieldValues>({
  name,
  control,
  rules,
  defaultValue,
  shouldUnregister,
  ...inputProps
}: FormInputProps<T>) {
  const {
    field,
    fieldState: { error },
  } = useController({
    name,
    control,
    rules,
    defaultValue,
    shouldUnregister,
  })

  return <Input {...inputProps} {...field} error={error?.message} />
}

// FormSelect - integrates Select with react-hook-form
export interface FormSelectProps<T extends FieldValues>
  extends Omit<SelectProps, 'name'>,
    UseControllerProps<T> {}

export function FormSelect<T extends FieldValues>({
  name,
  control,
  rules,
  defaultValue,
  shouldUnregister,
  ...selectProps
}: FormSelectProps<T>) {
  const {
    field,
    fieldState: { error },
  } = useController({
    name,
    control,
    rules,
    defaultValue,
    shouldUnregister,
  })

  return <Select {...selectProps} {...field} error={error?.message} />
}

// FormTextarea - integrates Textarea with react-hook-form
export interface FormTextareaProps<T extends FieldValues>
  extends Omit<TextareaProps, 'name'>,
    UseControllerProps<T> {}

export function FormTextarea<T extends FieldValues>({
  name,
  control,
  rules,
  defaultValue,
  shouldUnregister,
  ...textareaProps
}: FormTextareaProps<T>) {
  const {
    field,
    fieldState: { error },
  } = useController({
    name,
    control,
    rules,
    defaultValue,
    shouldUnregister,
  })

  return <Textarea {...textareaProps} {...field} error={error?.message} />
}
