---
name: react-hook-form-ts
description: "React Hook Form + Zod validation patterns for type-safe forms. Use when building forms with validation, multi-step wizards, dynamic fields, file uploads, or integrating forms with API mutations. Covers Zod schema design, field-level errors, and accessible form patterns."
---

# React Hook Form + Zod (TypeScript)

Type-safe form handling with React Hook Form v7 and Zod schema validation.

## When to Use This Skill

- Building forms with client-side validation
- Defining Zod schemas for form inputs
- Multi-step/wizard forms
- Dynamic field arrays
- File upload forms
- Integrating form submission with TanStack Query mutations
- Accessible form error display

## Prerequisites

```bash
pnpm add react-hook-form zod @hookform/resolvers
```

## Core Pattern: Schema → Form → Submit

### 1. Define Zod Schema (Source of Truth)

```typescript
// schemas/userForm.ts
import { z } from 'zod';

export const UserFormSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100),
  email: z.string().email('Invalid email address'),
  role: z.enum(['admin', 'user', 'viewer'], {
    errorMap: () => ({ message: 'Select a valid role' }),
  }),
  bio: z.string().max(500).optional(),
  password: z.string().min(8, 'Minimum 8 characters'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'], // Error appears on confirmPassword field
});

// Infer TypeScript type from schema
export type UserFormInput = z.infer<typeof UserFormSchema>;
```

### 2. Build the Form

```tsx
// components/UserForm.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { UserFormSchema, type UserFormInput } from '@/schemas/userForm';

function UserForm({ onSubmit }: { onSubmit: (data: UserFormInput) => void }) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<UserFormInput>({
    resolver: zodResolver(UserFormSchema),
    defaultValues: { name: '', email: '', role: 'user', bio: '' },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <FormField label="Name" error={errors.name?.message}>
        <input {...register('name')} id="name" />
      </FormField>

      <FormField label="Email" error={errors.email?.message}>
        <input {...register('email')} id="email" type="email" />
      </FormField>

      <FormField label="Role" error={errors.role?.message}>
        <select {...register('role')} id="role">
          <option value="user">User</option>
          <option value="admin">Admin</option>
          <option value="viewer">Viewer</option>
        </select>
      </FormField>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Saving...' : 'Save'}
      </button>
    </form>
  );
}
```

### 3. Accessible FormField Component

```tsx
interface FormFieldProps {
  label: string;
  error?: string;
  children: ReactNode;
}

function FormField({ label, error, children }: FormFieldProps) {
  // Derive IDs from children's id prop
  const childId = (children as React.ReactElement)?.props?.id;
  const errorId = childId ? `${childId}-error` : undefined;

  return (
    <div>
      <label htmlFor={childId}>{label}</label>
      {React.cloneElement(children as React.ReactElement, {
        'aria-invalid': !!error,
        'aria-describedby': error ? errorId : undefined,
      })}
      {error && (
        <span id={errorId} role="alert">
          {error}
        </span>
      )}
    </div>
  );
}
```

## Validation Timing

```typescript
const form = useForm<UserFormInput>({
  resolver: zodResolver(UserFormSchema),
  mode: 'onBlur',          // Validate on blur (recommended default)
  reValidateMode: 'onChange', // Re-validate on change after first error
});
```

| Mode | When | UX Impact |
|------|------|-----------|
| `onBlur` | Field loses focus | Best default — not distracting |
| `onSubmit` | Form submit only | Simple forms |
| `onChange` | Every keystroke | Avoid — poor UX, use only for search/autocomplete |
| `onTouched` | First blur, then onChange | Good for long forms |

## Integration with TanStack Query

```tsx
import { useMutation, useQueryClient } from '@tanstack/react-query';

function CreateUserForm() {
  const queryClient = useQueryClient();
  const form = useForm<UserFormInput>({
    resolver: zodResolver(UserFormSchema),
  });

  const createUser = useMutation({
    mutationFn: (data: UserFormInput) => api.users.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      form.reset(); // Clear form after success
    },
    onError: (error: ApiError) => {
      // Map server errors to form fields
      if (error.fieldErrors) {
        for (const [field, message] of Object.entries(error.fieldErrors)) {
          form.setError(field as keyof UserFormInput, { message });
        }
      }
    },
  });

  return (
    <form onSubmit={form.handleSubmit((data) => createUser.mutate(data))}>
      {/* fields */}
      {createUser.error && !createUser.error.fieldErrors && (
        <div role="alert">{createUser.error.message}</div>
      )}
    </form>
  );
}
```

## Advanced Patterns

### Dynamic Field Arrays

```tsx
import { useFieldArray } from 'react-hook-form';

const TagsSchema = z.object({
  tags: z.array(z.object({
    name: z.string().min(1, 'Tag name required'),
  })).min(1, 'At least one tag'),
});

function TagsForm() {
  const { control, register } = useForm({
    resolver: zodResolver(TagsSchema),
    defaultValues: { tags: [{ name: '' }] },
  });

  const { fields, append, remove } = useFieldArray({ control, name: 'tags' });

  return (
    <div>
      {fields.map((field, index) => (
        <div key={field.id}>
          <input {...register(`tags.${index}.name`)} />
          <button type="button" onClick={() => remove(index)}>Remove</button>
        </div>
      ))}
      <button type="button" onClick={() => append({ name: '' })}>Add Tag</button>
    </div>
  );
}
```

### Edit Form with Pre-filled Data

```tsx
function EditUserForm({ userId }: { userId: string }) {
  const { data: user } = useSuspenseQuery({
    queryKey: ['users', userId],
    queryFn: () => api.users.get(userId),
  });

  const form = useForm<UserFormInput>({
    resolver: zodResolver(UserFormSchema),
    defaultValues: user, // Pre-fill from server data
  });

  // Reset form when server data changes
  useEffect(() => {
    form.reset(user);
  }, [user, form]);
}
```

### Conditional Validation

```typescript
const ContactSchema = z.discriminatedUnion('contactMethod', [
  z.object({
    contactMethod: z.literal('email'),
    email: z.string().email(),
  }),
  z.object({
    contactMethod: z.literal('phone'),
    phone: z.string().regex(/^\+?[\d\s-]{10,}$/, 'Invalid phone number'),
  }),
]);
```

### File Upload

```tsx
const FileSchema = z.object({
  file: z
    .instanceof(FileList)
    .refine((files) => files.length > 0, 'File is required')
    .refine((files) => files[0]?.size <= 5_000_000, 'Max 5MB')
    .refine(
      (files) => ['image/png', 'image/jpeg'].includes(files[0]?.type),
      'Only PNG/JPEG allowed'
    ),
});

function UploadForm() {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(FileSchema),
  });

  return (
    <form onSubmit={handleSubmit((data) => { /* upload data.file[0] */ })}>
      <input type="file" accept="image/png,image/jpeg" {...register('file')} />
      {errors.file && <span role="alert">{errors.file.message}</span>}
    </form>
  );
}
```

## Zod Schema Patterns

### Shared Refinements

```typescript
// Reusable validators
const nonEmpty = z.string().min(1, 'Required');
const slug = z.string().regex(/^[a-z0-9-]+$/, 'Lowercase, numbers, hyphens only');
const currency = z.number().multipleOf(0.01).nonnegative();

// Compose into form schemas
const ProductSchema = z.object({
  name: nonEmpty.max(200),
  slug: slug,
  price: currency,
});
```

### Transform for API Submission

```typescript
const FormSchema = z.object({
  price: z.string().transform((v) => parseFloat(v)), // String input → number for API
  startDate: z.string().transform((v) => new Date(v).toISOString()),
});
```

### Server Error Mapping

```typescript
// Map backend validation errors to Zod format
function mapServerErrors(errors: Record<string, string[]>): z.ZodIssue[] {
  return Object.entries(errors).flatMap(([path, messages]) =>
    messages.map((message) => ({
      code: 'custom' as const,
      path: [path],
      message,
    }))
  );
}
```

## Error Display Patterns

| Error Type | Display | How |
|-----------|---------|-----|
| Field-level | Inline below input | `errors.fieldName?.message` with `role="alert"` |
| Cross-field (refinement) | Below related fields | Map to specific path in `.refine()` |
| Server validation | Inline via `setError` | Map 422 response fields to form errors |
| Network/auth error | Top-level banner | `mutation.error` outside form fields |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Validation on every keystroke | Use `mode: 'onBlur'` (default) |
| Missing `noValidate` on `<form>` | Add it — browser validation conflicts with RHF |
| Not resetting form after success | Call `form.reset()` in mutation `onSuccess` |
| Zod schema not matching form defaults | Ensure `defaultValues` satisfies the schema shape |
| `errors.field` without `?.message` | Always use optional chain — error may not exist |
| File input without `accept` attribute | Add `accept` for UX + validate in Zod for security |
