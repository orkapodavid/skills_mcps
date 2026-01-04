import uuid
import json

class BatchRequestBuilder:
    """
    Helper to build OData $batch requests.
    This is a simplified implementation supporting changeset for transactional integrity.
    """

    def __init__(self, client):
        self.client = client
        self.batch_id = f"batch_{uuid.uuid4()}"
        self.changeset_id = f"changeset_{uuid.uuid4()}"
        self.requests = []

    def add_request(self, method: str, url: str, body: dict = None, content_id: int = None):
        """
        Adds a request to the batch.
        Note: url should be relative to base URL (e.g. "accounts").
        """
        self.requests.append({
            "method": method,
            "url": url,
            "body": body,
            "content_id": content_id
        })

    def build_payload(self) -> str:
        """
        Constructs the multipart/mixed body.
        """
        lines = []

        # Start Batch
        lines.append(f"--{self.batch_id}")

        # Start Changeset (atomicity)
        # GET requests usually go outside changeset in batch, but CUD must be in changeset.
        # For simplicity, we put everything in a changeset if it's not GET?
        # Actually, Dataverse supports mixing.
        # Let's wrap everything in one changeset for now as that's the most common use case for batch (transactions).

        lines.append(f"Content-Type: multipart/mixed; boundary={self.changeset_id}")
        lines.append("")

        for req in self.requests:
            lines.append(f"--{self.changeset_id}")
            lines.append("Content-Type: application/http")
            lines.append("Content-Transfer-Encoding: binary")
            if req.get("content_id"):
                lines.append(f"Content-ID: {req['content_id']}")
            lines.append("")

            # Request Line
            # Must be absolute URL or relative?
            # OData spec says relative to service root.
            # But the client is configured with full URL.
            # We assume user passes relative path like "accounts".
            # The URL in batch must be relative to the $batch URL context, usually.

            lines.append(f"{req['method']} {req['url']} HTTP/1.1")
            lines.append("Content-Type: application/json; type=entry")
            lines.append("")

            if req.get("body"):
                lines.append(json.dumps(req["body"]))
                lines.append("")

        lines.append(f"--{self.changeset_id}--")
        lines.append(f"--{self.batch_id}--")

        return "\r\n".join(lines)

    def execute(self):
        """
        Executes the batch request.
        """
        payload = self.build_payload()
        headers = {
            "Content-Type": f"multipart/mixed; boundary={self.batch_id}",
            "Accept": "application/json"
        }

        # $batch endpoint
        return self.client._make_request("POST", "$batch", data=payload, headers=headers)
