# Sharing Your Spreadsheet with the Service Account

## Critical Step for Affiliate Integration

For the affiliate product integration to work correctly, you **must** share your Google Spreadsheet with our service account email address.

## Step-by-Step Instructions

1. Open your Google Spreadsheet that contains affiliate products
2. Click the "**Share**" button in the top-right corner
   ![Share Button](https://storage.googleapis.com/support-kms-prod/SNP_ACAF591C26E64B7B67570525A4DF541F88F1_4289852_en_v1)

3. Enter this exact service account email address:

   ```
   blogs-monetizer-152@blogs-monetizer.iam.gserviceaccount.com
   ```

4. Set permission to "**Editor**"
   ![Permission Setting](https://storage.googleapis.com/support-kms-prod/SNP_C9C8FCCC0EDEDBB1C253AE555E4402FEAFC1_4289984_en_v1)

5. Uncheck "Notify people" (optional)
6. Click "**Send**"

## Verify Sharing Settings

After sharing, you can verify the setting:

1. Click the "**Share**" button again
2. Click "**Manage people and links**"
3. Check that the service account email is listed with "Editor" access

## Common Issues

If you're seeing error messages like:

```
Error: The service account doesn't have permission to access this spreadsheet
```

This means you either:

- Haven't shared the spreadsheet with the service account
- Shared it with a different email address
- Only gave "Viewer" access instead of "Editor"

## Why This is Necessary

The service account acts as a separate Google user that our application uses to access your spreadsheet programmatically. Without explicit sharing permissions, Google will block access attempts, resulting in permission errors.

## Need Help?

If you're still encountering issues after sharing your spreadsheet, please check:

1. The spreadsheet URL in your `.env` file is correct
2. The service account email is exactly as shown above
3. Your Google account has permission to share the spreadsheet
