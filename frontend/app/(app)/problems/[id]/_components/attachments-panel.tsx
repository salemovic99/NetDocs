"use client";

import * as React from "react";
import { Download, FileText, Loader2, Trash2, Upload } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AvStatusBadge } from "@/components/shared/badges";
import { ConfirmDialog } from "@/components/shared/confirm-dialog";
import { usePermissions } from "@/lib/auth/session-context";
import {
  attachmentDownloadUrl,
  useDeleteAttachment,
  useProblemAttachments,
  useUploadAttachment,
} from "@/lib/hooks/use-attachments";
import { PERMISSIONS } from "@/lib/permissions";

function formatBytes(n: number) {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / 1024 / 1024).toFixed(1)} MB`;
}

export function AttachmentsPanel({ problemId }: { problemId: string }) {
  const { can } = usePermissions();
  const { data, isLoading } = useProblemAttachments(problemId);
  const upload = useUploadAttachment("problems", problemId);
  const remove = useDeleteAttachment();
  const inputRef = React.useRef<HTMLInputElement>(null);

  const canUpload = can(PERMISSIONS.ATTACHMENTS_UPLOAD);
  const canDownload = can(PERMISSIONS.ATTACHMENTS_DOWNLOAD);

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between">
        <CardTitle className="text-h4">Attachments</CardTitle>
        {canUpload ? (
          <>
            <input
              ref={inputRef}
              type="file"
              hidden
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) upload.mutate(file);
                e.target.value = "";
              }}
            />
            <Button
              variant="outline"
              size="sm"
              onClick={() => inputRef.current?.click()}
              disabled={upload.isPending}
            >
              {upload.isPending ? (
                <Loader2 className="animate-spin" />
              ) : (
                <Upload />
              )}
              Upload
            </Button>
          </>
        ) : null}
      </CardHeader>
      <CardContent className="space-y-2">
        {isLoading ? (
          <p className="text-body-sm text-on-surface-variant">Loading…</p>
        ) : !data?.length ? (
          <p className="text-body-sm text-on-surface-variant">
            No attachments. Allowed: images, PDF, logs, configs (max 25 MB).
          </p>
        ) : (
          data.map((a) => (
            <div
              key={a.id}
              className="flex items-center gap-3 rounded-md border border-border bg-surface-container-low px-3 py-2"
            >
              <FileText className="size-4 shrink-0 text-on-surface-variant" />
              <div className="min-w-0 flex-1">
                <p className="truncate text-body-lg text-on-surface">
                  {a.filename}
                </p>
                <p className="text-body-sm text-on-surface-variant">
                  {formatBytes(a.size_bytes)}
                </p>
              </div>
              <AvStatusBadge status={a.av_status} />
              {canDownload && a.av_status === "clean" ? (
                <Button variant="ghost" size="icon-sm" asChild>
                  <a href={attachmentDownloadUrl(a.id)} download>
                    <Download />
                  </a>
                </Button>
              ) : null}
              {canUpload ? (
                <ConfirmDialog
                  trigger={
                    <Button variant="ghost" size="icon-sm">
                      <Trash2 className="text-error" />
                    </Button>
                  }
                  title="Delete attachment?"
                  description={a.filename}
                  confirmLabel="Delete"
                  onConfirm={() => remove.mutate(a.id)}
                />
              ) : null}
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
