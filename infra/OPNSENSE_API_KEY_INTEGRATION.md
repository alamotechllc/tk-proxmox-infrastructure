# OPNsense API Key Integration Guide

## 🔑 **API Key Integration Steps**

### **Step 1: Locate Your API Key File**

Your OPNsense API key file should contain:
- **API Key**: Usually a long string of characters
- **API Secret**: Another string of characters
- **Permissions**: List of granted permissions
- **IP Restrictions**: Any IP limitations

### **Step 2: Extract API Credentials**

The API key file typically contains information like:
```
API Key: abc123def456ghi789...
API Secret: xyz789uvw456rst123...
Permissions: core/firewall, core/dhcp, core/interface
IP Restrictions: 172.23.7.0/24
```

### **Step 3: Add to Semaphore Secrets**

1. **Access Semaphore UI**: http://172.23.5.22:3000
2. **Navigate to**: Project Settings → Secrets
3. **Create New Secret**:
   - **Name**: `OPNsense API Key`
   - **Type**: `Text`
   - **Value**: Copy the API Key from your file
4. **Create Second Secret**:
   - **Name**: `OPNsense API Secret`
   - **Type**: `Password`
   - **Value**: Copy the API Secret from your file

### **Step 4: Test API Connectivity**

Once you've added the secrets, we can test the API connection:

```bash
# Test command (replace with your actual credentials)
curl -k -u "your_api_key:your_api_secret" \
  https://172.23.7.1/api/core/system/info
```

### **Step 5: Deploy OPNsense Templates**

1. **Import Templates**: Use the `opnsense_template_config.json`
2. **Configure Secrets**: Link the API key secrets to templates
3. **Test Templates**: Run the OPNsense Firewall Management template

## 🔧 **Quick Setup Commands**

### **If you have the API key file:**

```bash
# Navigate to your project directory
cd /Users/mike.turner/APP_Projects/tk-proxmox

# Create a secure location for API keys
mkdir -p infra/secrets
chmod 700 infra/secrets

# Copy your API key file to the secrets directory
cp /path/to/your/api-key.txt infra/secrets/opnsense-api-key.txt
chmod 600 infra/secrets/opnsense-api-key.txt
```

### **Parse the API key file:**

```bash
# Extract API key and secret from the file
grep -i "api key" infra/secrets/opnsense-api-key.txt
grep -i "api secret" infra/secrets/opnsense-api-key.txt
```

## 🧪 **Test API Connection**

Once you have the credentials, we can test the connection:

```bash
# Test OPNsense API connectivity
curl -k -u "$(grep 'API Key' infra/secrets/opnsense-api-key.txt | cut -d':' -f2 | tr -d ' '):$(grep 'API Secret' infra/secrets/opnsense-api-key.txt | cut -d':' -f2 | tr -d ' ')" \
  https://172.23.7.1/api/core/system/info
```

## 📋 **Next Steps**

1. **Locate your API key file**
2. **Extract the API key and secret**
3. **Add them to Semaphore secrets**
4. **Test the API connection**
5. **Deploy the OPNsense templates**

## 🔒 **Security Best Practices**

- **Store API keys securely** in Semaphore secrets
- **Use IP restrictions** to limit API access
- **Rotate API keys** regularly
- **Monitor API usage** for security
- **Use HTTPS only** for API communications

---

**Please share the location of your API key file so I can help you integrate it into the system!** 🔑
