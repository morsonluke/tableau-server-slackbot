Local testing:

1. Export the environment variables:

```bash
export SLACK_SECRET=$SLACK_SIGNING_SECRET
export SLACK_API_TOKEN=$SLACK_BOT_TOKEN
export GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS
```

2. Run locally using the [Functions Framework](https://github.com/GoogleCloudPlatform/functions-framework-python)

```bash
functions-framework --target=handle_event
```

3. Start ngrok

```yaml
./ngrok http 8080
```

4. Update the Event Subscription configuration:

```bash
https://91eb01f51377.ngrok.io/slack/events
```

5. If require add this in ~/.bash_profile: 

```yaml
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
```

6. Create the zip file to capture on changes: 

```bash
make generate_zipfiles
```

