# Deploying to HuggingFace Spaces

This document provides detailed instructions on deploying the Blogs Monetizer to HuggingFace Spaces and keeping the Space active to prevent it from going to sleep due to inactivity.

## Deploying to HuggingFace Spaces

1. Create a new Space on HuggingFace with Docker template
2. Clone your Space repository locally
3. Add your Blogs Monetizer project to the cloned repository
4. Configure the environment variables in the Spaces UI:
   - `USE_SERVICE_ACCOUNT`: Set to "true"
   - `GOOGLE_SERVICE_ACCOUNT_INFO`: Your full service account JSON as a single line
   - `ENABLE_HEARTBEAT`: Set to "true" (enabled by default)
   - `HEARTBEAT_INTERVAL_MINUTES`: Set to desired interval (default: 15 minutes)
5. Push the changes to your Space repository
6. HuggingFace will automatically build and deploy your app

## Preventing Spaces from Sleeping

HuggingFace Spaces automatically go to sleep after periods of inactivity. The Blogs Monetizer includes a heartbeat mechanism to keep your Space active.

### How the Heartbeat Works

The heartbeat mechanism periodically generates a blog at regular intervals (default: every 15 minutes). This activity keeps the Space from going to sleep due to inactivity.

### Configuring the Heartbeat

1. `ENABLE_HEARTBEAT`: Set to "true" or "false" to enable or disable the heartbeat
2. `HEARTBEAT_INTERVAL_MINUTES`: Control how frequently blogs are generated (default: 15 minutes)

For optimal performance on free tier HuggingFace Spaces:

- A 15-minute interval is recommended to ensure the space stays active
- Adjust based on your specific needs and usage patterns

### Monitoring the Heartbeat

You can check the heartbeat status using:

```bash
python helpers/check_heartbeat.py --server "https://your-space-url.hf.space" --status
```

This will show:

- If the heartbeat is running
- When the last blog was generated
- When the next blog will be generated

### Manual Blog Generation

You can trigger blog generation manually:

```bash
python helpers/check_heartbeat.py --server "https://your-space-url.hf.space" --generate
```

## Troubleshooting

If your Space still goes to sleep:

1. Verify that `ENABLE_HEARTBEAT` is set to "true"
2. Check that `HEARTBEAT_INTERVAL_MINUTES` is set to a reasonable value (15 is recommended)
3. Make sure your blog generation process completes successfully within the heartbeat interval
4. Check the Space logs for any errors in the blog generation process

For persistent issues:

- Consider upgrading to a paid HuggingFace Space plan that doesn't sleep
- Implement external pinging service like UptimeRobot as a backup
