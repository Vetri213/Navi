# API Keys Setup Guide

This guide will help you obtain and configure all the API keys needed for Navi to function.

---

##  Required API Keys

Navi requires three API keys:

1. **Google Gemini API Key** - For AI vision and language understanding
2. **ElevenLabs API Key** - For speech recognition and voice synthesis
3. **Picovoice Access Key** - For wake word detection ("Hey Navi")

---

##  Google Gemini API Key

### What is it for?
Gemini analyzes screenshots and understands your requests to provide context-aware guidance.

### Getting Your Key

1. **Visit Google AI Studio**
   - Go to [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account

2. **Create API Key**
   - Click "Create API Key"
   - Select "Create API key in new project" or choose an existing project
   - Copy the generated key

3. **Add to .env file**
   ```env
   GEMINI_API_KEY=AIzaSyBcJInJfu-CZzbgr0FyCDaBeoSYlI3ys5A
   ```

### Free Tier Limits
- **60 requests per minute**
- **1,500 requests per day**
- **1 million tokens per month**

Perfect for personal use! 

### Troubleshooting
- **Error: "API key not valid"**
  - Ensure you copied the entire key
  - Check for extra spaces or quotes
  - Verify the key is enabled in Google Cloud Console

- **Error: "Quota exceeded"**
  - You've hit the free tier limit
  - Wait for the quota to reset (daily/monthly)
  - Consider upgrading to paid tier if needed

---

##  ElevenLabs API Key

### What is it for?
ElevenLabs provides:
- **Speech-to-Text:** Converts your voice to text
- **Text-to-Speech:** Navi's natural voice responses

### Getting Your Key

1. **Create Account**
   - Visit [https://elevenlabs.io/](https://elevenlabs.io/)
   - Click "Sign Up" (free account available)
   - Verify your email

2. **Navigate to Profile**
   - Click your profile icon (top right)
   - Select "Profile + API Key"

3. **Generate API Key**
   - Click "Generate API Key" or copy existing key
   - **Important:** Ensure the key has `speech_to_text` permission enabled

4. **Add to .env file**
   ```env
   ELEVEN_API_KEY=sk_b5640018399c9a4843242e221f6ec92a7696aa0ddeba4953
   ```

### Free Tier Limits
- **10,000 characters per month** for text-to-speech
- **Speech-to-text** usage varies by plan

### Checking Permissions

Your API key must have **speech-to-text** permission:

1. Go to [ElevenLabs Dashboard](https://elevenlabs.io/app/speech-synthesis)
2. Check your subscription includes "Speech to Speech" or "Speech to Text"
3. If not, upgrade your plan or create a new key with proper permissions

### Troubleshooting

- **Error: "missing_permissions speech_to_text"**
  - Your API key doesn't have speech-to-text enabled
  - Create a new API key with proper permissions
  - Or upgrade your ElevenLabs subscription

- **Error: "401 Unauthorized"**
  - API key is invalid or expired
  - Generate a new key from your profile

- **Error: "Quota exceeded"**
  - You've used your monthly character limit
  - Wait for monthly reset or upgrade plan

---

##  Picovoice Access Key

### What is it for?
Picovoice Porcupine enables wake word detection, so Navi responds when you say "Hey Navi".

### Getting Your Key

1. **Create Account**
   - Visit [https://console.picovoice.ai/](https://console.picovoice.ai/)
   - Sign up for a free account
   - Verify your email

2. **Access Console**
   - Log in to Picovoice Console
   - You'll see your dashboard

3. **Generate Access Key**
   - Look for "Access Key" section
   - Click "Generate" or copy existing key
   - The key will look like: `0/jfRzAai0MbCufJv8sQmVt00I+klJFjKAhA/X4S8+FT5RncEEmgQQ==`

4. **Add to .env file**
   ```env
   PICOVOICE_ACCESS_KEY=0/jfRzAai0MbCufJv8sQmVt00I+klJFjKAhA/X4S8+FT5RncEEmgQQ==
   ```

### Free Tier Limits
- **3 wake word models**
- **Unlimited local processing** (no cloud usage limits!)

### Troubleshooting

- **Error: "Picovoice Error (code 00000136)"**
  - Invalid access key
  - Copy the key again carefully
  - Ensure no extra spaces or characters

- **Error: "Wake word model not found"**
  - The `Hey-Navi_en_mac_v3_0_0.ppn` file is missing
  - Ensure you cloned the full repository
  - Check the file exists in the project directory

---

##  Complete .env File Example

Your `.env` file should look like this:

```env
GEMINI_API_KEY=AIzaSyBcJInJfu-CZzbgr0FyCDaBeoSYlI3ys5A
ELEVEN_API_KEY=sk_b5640018399c9a4843242e221f6ec92a7696aa0ddeba4953
PICOVOICE_ACCESS_KEY=0/jfRzAai0MbCufJv8sQmVt00I+klJFjKAhA/X4S8+FT5RncEEmgQQ==
```

### Important Notes

- **No quotes needed** around the values
- **No spaces** before or after the `=` sign
- **One key per line**
- **Keep this file private** - never commit to Git!

---

##  Security Best Practices

### Protecting Your API Keys

1. **Never commit .env to Git**
   - The `.gitignore` file should include `.env`
   - Verify with: `git status` (should not show .env)

2. **Don't share keys publicly**
   - Never post keys in issues, forums, or chat
   - Regenerate immediately if accidentally exposed

3. **Use environment variables in production**
   - For deployed applications, use secure environment variable storage
   - Examples: Heroku Config Vars, AWS Secrets Manager

4. **Regenerate keys periodically**
   - Change keys every 3-6 months
   - Immediately regenerate if compromised

### What if My Key is Exposed?

1. **Immediately revoke the key** in the respective service dashboard
2. **Generate a new key**
3. **Update your .env file**
4. **Monitor usage** for any unauthorized activity

---

##  Cost Considerations

### Free Tier Summary

| Service | Free Tier | Sufficient for Navi? |
|---------|-----------|---------------------|
| **Gemini** | 1M tokens/month |  Yes, for personal use |
| **ElevenLabs** | 10K chars/month |  Moderate use only |
| **Picovoice** | Unlimited local |  Yes, completely free |

### When to Upgrade

Consider paid plans if:
- Using Navi **multiple hours per day**
- Supporting **multiple users**
- Need **higher quality voices** (ElevenLabs)
- Require **faster response times**

### Estimated Costs (Paid Tiers)

- **Gemini:** Pay-as-you-go, ~$0.001 per 1K tokens
- **ElevenLabs:** $5-$22/month for higher limits
- **Picovoice:** Free for most use cases

---

##  Verification Checklist

After setting up your API keys:

- [ ] `.env` file created in project root
- [ ] All three API keys added
- [ ] No quotes around values
- [ ] No extra spaces
- [ ] File saved
- [ ] Navi starts without "API key missing" errors
- [ ] Wake word detection works
- [ ] Voice recognition works
- [ ] Voice responses work

---

##  Testing Your Setup

Run this test to verify all keys are working:

```bash
python main.py
```

Expected output:
```
 Loading .env from: /path/to/.env
 ELEVEN_API_KEY loaded: Yes
 Found wake word model
 Wake word detection started successfully!
 Wake word detection active. Say 'Hey Navi' to activate...
```

Then say **"Hey Navi"** and ask a question to test all components.

---

##  Still Having Issues?

- Check the [Troubleshooting Guide](Troubleshooting.md)
- Review [Installation Guide](Installation-Guide.md)
- Open an issue on [GitHub](https://github.com/Vetri213/Navi/issues)

---

**Next Step:** [Quick Start Guide](Quick-Start.md) to begin using Navi!
