# Doorbel to Botsquad

- Watches the ring doorbell history for recent 'ding' events
- Downloads latest recording from the camera
- Convert it to an animated gif (ffmpeg required)
- Uploads gif to Google Cloud Storage
- Sends chat event with gif URL to a Botsquad bot

## Installation

1. Install `ffmpeg`.

2. Python deps:

```
  pip install -r requirements.txt
```

3. Also, `config.json` should contain something like:

```
{
  "gcs_bucket": "bucket-name",
  "gcs_bucket_prefix": "some-prefix/",
  "bot_id": "ea09f8ea-098a0-8fe0a8ea0-98f09a8",
  "api_key": "fldsjafoiadsjfoirewjforew"
}

```

4. Furthermore, a `gcs-credentials.json` file must exist in the same directory
   which contains the service account credentials for writing the gif file to GCS.
