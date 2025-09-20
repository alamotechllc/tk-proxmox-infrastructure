# 🔒 Security Migration Guide: Environment Variables → Secrets

## 🎯 Overview

You're absolutely right! Using **Secrets** instead of **Environment Variables** is a much better security practice. This guide shows how to migrate all sensitive credentials to Semaphore's secure secret storage.

## 🔐 Security Benefits of Secrets vs Environment Variables

### **✅ Secrets (Recommended)**
- **🔒 Encrypted Storage**: Secrets are encrypted at rest
- **🔍 Access Control**: Fine-grained access permissions
- **📋 Audit Trail**: Who accessed what secret when
- **🔄 Rotation**: Easy credential rotation
- **👁️ No Exposure**: Never visible in logs or UI
- **🔑 Role-Based**: Different secrets for different roles

### **❌ Environment Variables (Current - Less Secure)**
- **📝 Plain Text**: Stored in plain text JSON
- **👀 Visible**: Can be seen in UI and logs
- **📋 Limited Audit**: Basic access tracking
- **🔄 Manual Rotation**: Requires manual updates
- **🌍 Global Scope**: Available to all playbooks

---

## 🔄 Migration Plan

### **Phase 1: Create Network Device Secrets**

#### **🔌 Arista Switch Secrets**
```bash
# Via Semaphore Web Interface:
# Project → Network Infrastructure → Keys → Add Key

1. Arista Admin Credentials
   Type: Login/Password
   Name: "Arista Admin Credentials"
   Login: admin
   Password: [Your Arista Password]

2. Arista Enable Password
   Type: Password
   Name: "Arista Enable Password"
   Password: [Your Arista Enable Password]

3. Arista API Credentials
   Type: Login/Password
   Name: "Arista eAPI Credentials"
   Login: eapi_user
   Password: [Your eAPI Password]
```

#### **🔌 Cisco Nexus Secrets**
```bash
1. Nexus Admin Credentials
   Type: Login/Password
   Name: "Nexus Admin Credentials"
   Login: admin
   Password: [Your Nexus Password]

2. Nexus SNMP Community
   Type: Password
   Name: "Nexus SNMP Community"
   Password: [Your SNMP Community String]
```

#### **🔌 Cisco Catalyst Secrets**
```bash
1. Catalyst Admin Credentials
   Type: Login/Password
   Name: "Catalyst Admin Credentials"
   Login: admin
   Password: [Your Catalyst Password]

2. Catalyst Enable Password
   Type: Password
   Name: "Catalyst Enable Password"
   Password: [Your Enable Password]

3. Catalyst SNMP Community
   Type: Password
   Name: "Catalyst SNMP Community"
   Password: [Your SNMP Community String]
```

### **Phase 2: Create Firewall Secrets**

#### **🔥 OPNsense Secrets**
```bash
1. OPNsense Admin Credentials
   Type: Login/Password
   Name: "OPNsense Admin Credentials"
   Login: admin
   Password: 8fewWER8382  # Your actual password

2. OPNsense API Credentials
   Type: Login/Password
   Name: "OPNsense API Credentials"
   Login: [API Key]
   Password: [API Secret]

3. OPNsense SSH Access
   Type: SSH Key or Login/Password
   Name: "OPNsense SSH Access"
   [Your SSH credentials]
```

### **Phase 3: Create Service Secrets**

#### **📊 Monitoring & Backup Secrets**
```bash
1. Backup Server Credentials
   Type: Login/Password
   Name: "Network Backup Credentials"
   Login: netbackup
   Password: [Your Backup Password]

2. Monitoring Database
   Type: Login/Password
   Name: "NMS Database Credentials"
   Login: nms_user
   Password: [Your DB Password]
```

---

## 🔧 How to Create Secrets in Semaphore

### **Method 1: Web Interface (Recommended)**
1. **Navigate**: http://172.23.5.22:3000
2. **Login**: `admin` / `8fewWER8382`
3. **Go to**: Network Infrastructure project
4. **Click**: "Keys" tab
5. **Click**: "Add Key" button
6. **Fill out**:
   - **Name**: Descriptive name (e.g., "Arista Admin Credentials")
   - **Type**: Choose appropriate type:
     - `login_password` - For username/password pairs
     - `password` - For single passwords/tokens
     - `ssh` - For SSH private keys
   - **Credentials**: Enter actual values

### **Method 2: API (I can help)**
Once you provide the actual credentials, I can create them via API:

```bash
# Example API call structure:
curl "http://172.23.5.22:3000/api/project/4/keys" -X POST \
  -H "Cookie: $COOKIE" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 4,
    "name": "Arista Admin Credentials",
    "type": "login_password",
    "login_password": {
      "login": "admin",
      "password": "your_actual_password"
    }
  }'
```

---

## 📝 Updated Playbook Syntax

### **Before (Environment Variables):**
```yaml
# OLD - Less secure
vars:
  ansible_user: "{{ lookup('env', 'ARISTA_ADMIN_USER') }}"
  ansible_password: "{{ lookup('env', 'ARISTA_ADMIN_PASS') }}"
  ansible_become_password: "{{ lookup('env', 'ARISTA_ENABLE_PASS') }}"
```

### **After (Secrets):**
```yaml
# NEW - More secure
vars:
  ansible_user: "{{ arista_admin_credentials.login }}"
  ansible_password: "{{ arista_admin_credentials.password }}"
  ansible_become_password: "{{ arista_enable_password.password }}"
```

---

## 🔄 Migration Steps

### **Step 1: Create All Secrets**
I can help you create these secrets via API once you provide the actual credentials, or you can create them via the web interface.

### **Step 2: Update Playbooks**
I'll update all playbooks to reference secrets instead of environment variables:
- `backup_switches.yml`
- `vlan_port_assignment.yml`
- `port_management.yml`
- All network automation playbooks

### **Step 3: Update Inventories**
I'll update inventory files to reference secrets:
- Core Network Infrastructure
- Security Infrastructure
- All device authentication references

### **Step 4: Remove Old Environment Variables**
After migration is complete and tested, I'll remove the old environment variables.

### **Step 5: Test & Validate**
Test all operations to ensure secrets are working properly.

---

## 🎯 **Recommended Secret Structure**

### **🔌 Network Device Secrets:**
```
1. "Arista Admin Credentials" (login_password)
2. "Arista Enable Password" (password)
3. "Nexus Admin Credentials" (login_password)
4. "Catalyst Admin Credentials" (login_password)
5. "Catalyst Enable Password" (password)
```

### **🔥 Security Device Secrets:**
```
6. "OPNsense Admin Credentials" (login_password)
7. "OPNsense API Credentials" (login_password)
8. "OPNsense SSH Key" (ssh)
```

### **📊 Service Secrets:**
```
9. "Network Backup Credentials" (login_password)
10. "SNMP Communities" (password)
11. "Monitoring Database" (login_password)
```

---

## 🚀 **Ready to Migrate?**

**I can help you migrate in two ways:**

### **Option 1: Provide Credentials (I'll create secrets via API)**
Share your actual device credentials and I'll create all the secrets programmatically.

### **Option 2: Manual Creation (I'll provide guidance)**
I'll guide you through creating each secret in the web interface and then update all the playbooks.

**Which approach would you prefer?** 

Once we migrate to secrets, your network infrastructure will have **enterprise-grade credential security** with encrypted storage, access control, and audit trails! 🔒
