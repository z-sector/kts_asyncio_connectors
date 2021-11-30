from typing import List, Optional


class MultipartUploader:
    def __init__(self, client, bucket: str, key: str) -> None:
        self.client = client
        self.bucket = bucket
        self.key = key

        self.part_number: int = 0
        self.parts: List[dict] = []
        self.mpu: Optional[dict] = None
        self.uploaded_size: float = 0
        self.is_loading: bool = False

    async def __aenter__(self):
        await self._create_uploading()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if not exc_type:
            await self._finish_uploading()
        else:
            await self.client.abort_multipart_upload(
                Bucket=self.bucket,
                Key=self.key,
                UploadId=self.mpu["UploadId"],
            )

    async def _create_uploading(self) -> None:
        self.parts = []
        self.part_number = 1

        self.mpu = await self.client.create_multipart_upload(
            Bucket=self.bucket,
            Key=self.key,
        )

        self.is_loading = True
        self.uploaded_size = 0

    async def upload_part(self, chunk: bytes) -> None:
        part = await self.client.upload_part(
            Bucket=self.bucket,
            Key=self.key,
            PartNumber=self.part_number,
            UploadId=self.mpu["UploadId"],
            Body=chunk,
        )

        self.parts.append({"PartNumber": self.part_number, "ETag": part["ETag"]})
        self.part_number += 1

        self.uploaded_size += len(chunk) / 1024 / 1024
        print(self.uploaded_size)

    async def _finish_uploading(self) -> None:
        part_info = {"Parts": self.parts}
        await self.client.complete_multipart_upload(
            Bucket=self.bucket,
            Key=self.key,
            UploadId=self.mpu["UploadId"],
            MultipartUpload=part_info,
        )
        self.is_loading = False
