"use client";

import { Toaster as Sonner } from "sonner";

type ToasterProps = React.ComponentProps<typeof Sonner>;

function Toaster(props: ToasterProps) {
  return (
    <Sonner
      theme="dark"
      position="bottom-right"
      toastOptions={{
        classNames: {
          toast:
            "group rounded-md border border-border bg-popover text-popover-foreground shadow-lg",
          description: "text-on-surface-variant",
          actionButton: "bg-primary-container text-primary-foreground",
          cancelButton: "bg-surface-container-high text-on-surface",
          error: "text-error",
          success: "text-success",
        },
      }}
      {...props}
    />
  );
}

export { Toaster };
