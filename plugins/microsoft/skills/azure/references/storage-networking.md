# Storage & Networking

Storage accounts, virtual networks, network security groups, public IPs, and load balancers via Azure Resource Manager.

## Contents

- [Storage Accounts](#storage-accounts)
  - [List Storage Accounts](#list-storage-accounts)
  - [Create a Storage Account](#create-a-storage-account)
  - [Get a Storage Account](#get-a-storage-account)
  - [List Storage Account Keys](#list-storage-account-keys)
  - [Delete a Storage Account](#delete-a-storage-account)
- [Virtual Networks](#virtual-networks)
  - [List VNets](#list-vnets)
  - [Create a VNet](#create-a-vnet)
  - [Subnets](#subnets)
- [Network Security Groups](#network-security-groups)
  - [Create an NSG](#create-an-nsg)
  - [Add a Security Rule](#add-a-security-rule)
- [Public IP Addresses](#public-ip-addresses)
  - [Create a Public IP](#create-a-public-ip)
  - [List Public IPs](#list-public-ips)
- [Load Balancers](#load-balancers)
  - [Create a Load Balancer](#create-a-load-balancer)
  - [List Load Balancers](#list-load-balancers)
- [Network Interfaces](#network-interfaces)

## Storage Accounts

Provider: `Microsoft.Storage/storageAccounts`
api-version: `2023-05-01`

Base path:
```
/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts
```

### List Storage Accounts

```bash
curl -s 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts?api-version=2023-05-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

List all in subscription:
```bash
curl -s 'https://management.azure.com/subscriptions/{subId}/providers/Microsoft.Storage/storageAccounts?api-version=2023-05-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Create a Storage Account

```bash
curl -s -X PUT 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{accountName}?api-version=2023-05-01' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "eastus",
    "sku": { "name": "Standard_LRS" },
    "kind": "StorageV2",
    "properties": {
      "supportsHttpsTrafficOnly": true,
      "minimumTlsVersion": "TLS1_2"
    }
  }' | python3 -m json.tool
```

Storage account names must be globally unique, 3-24 chars, lowercase letters and numbers only.

Common SKUs: `Standard_LRS`, `Standard_GRS`, `Standard_ZRS`, `Premium_LRS`.

### Get a Storage Account

```bash
curl -s 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{accountName}?api-version=2023-05-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### List Storage Account Keys

```bash
curl -s -X POST 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{accountName}/listKeys?api-version=2023-05-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

Returns two access keys. Never display these to the user — mask them in output.

### Delete a Storage Account

```bash
curl -s -X DELETE 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{accountName}?api-version=2023-05-01' \
  -H "Authorization: Bearer $TOKEN"
```

## Virtual Networks

Provider: `Microsoft.Network/virtualNetworks`
api-version: `2024-01-01`

Base path:
```
/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Network/virtualNetworks
```

### List VNets

```bash
curl -s 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Network/virtualNetworks?api-version=2024-01-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Create a VNet

```bash
curl -s -X PUT 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Network/virtualNetworks/{vnetName}?api-version=2024-01-01' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "eastus",
    "properties": {
      "addressSpace": {
        "addressPrefixes": ["10.0.0.0/16"]
      },
      "subnets": [
        {
          "name": "default",
          "properties": {
            "addressPrefix": "10.0.0.0/24"
          }
        }
      ]
    }
  }' | python3 -m json.tool
```

### Subnets

List subnets:
```bash
curl -s 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Network/virtualNetworks/{vnetName}/subnets?api-version=2024-01-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

Create a subnet:
```bash
curl -s -X PUT 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Network/virtualNetworks/{vnetName}/subnets/{subnetName}?api-version=2024-01-01' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "addressPrefix": "10.0.1.0/24"
    }
  }' | python3 -m json.tool
```

## Network Security Groups

Provider: `Microsoft.Network/networkSecurityGroups`
api-version: `2024-01-01`

Base path:
```
/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Network/networkSecurityGroups
```

### Create an NSG

```bash
curl -s -X PUT 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Network/networkSecurityGroups/{nsgName}?api-version=2024-01-01' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "eastus",
    "properties": {
      "securityRules": [
        {
          "name": "allow-ssh",
          "properties": {
            "protocol": "Tcp",
            "sourcePortRange": "*",
            "destinationPortRange": "22",
            "sourceAddressPrefix": "*",
            "destinationAddressPrefix": "*",
            "access": "Allow",
            "priority": 100,
            "direction": "Inbound"
          }
        }
      ]
    }
  }' | python3 -m json.tool
```

### Add a Security Rule

```bash
curl -s -X PUT 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Network/networkSecurityGroups/{nsgName}/securityRules/{ruleName}?api-version=2024-01-01' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "protocol": "Tcp",
      "sourcePortRange": "*",
      "destinationPortRange": "443",
      "sourceAddressPrefix": "*",
      "destinationAddressPrefix": "*",
      "access": "Allow",
      "priority": 200,
      "direction": "Inbound"
    }
  }' | python3 -m json.tool
```

Priority values: 100-4096. Lower number = higher priority.

## Public IP Addresses

Provider: `Microsoft.Network/publicIPAddresses`
api-version: `2024-01-01`

### Create a Public IP

```bash
curl -s -X PUT 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Network/publicIPAddresses/{ipName}?api-version=2024-01-01' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "eastus",
    "sku": { "name": "Standard" },
    "properties": {
      "publicIPAllocationMethod": "Static"
    }
  }' | python3 -m json.tool
```

SKU `Standard` supports availability zones and is recommended for production. `Basic` is being retired.

### List Public IPs

```bash
curl -s 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Network/publicIPAddresses?api-version=2024-01-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

## Load Balancers

Provider: `Microsoft.Network/loadBalancers`
api-version: `2024-01-01`

### Create a Load Balancer

```bash
curl -s -X PUT 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Network/loadBalancers/{lbName}?api-version=2024-01-01' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "eastus",
    "sku": { "name": "Standard" },
    "properties": {
      "frontendIPConfigurations": [
        {
          "name": "frontend",
          "properties": {
            "publicIPAddress": {
              "id": "/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Network/publicIPAddresses/{ipName}"
            }
          }
        }
      ],
      "backendAddressPools": [
        { "name": "backend-pool" }
      ],
      "probes": [
        {
          "name": "health-probe",
          "properties": {
            "protocol": "Http",
            "port": 80,
            "requestPath": "/health",
            "intervalInSeconds": 15,
            "numberOfProbes": 2
          }
        }
      ],
      "loadBalancingRules": [
        {
          "name": "http-rule",
          "properties": {
            "frontendIPConfiguration": {
              "id": "/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Network/loadBalancers/{lbName}/frontendIPConfigurations/frontend"
            },
            "backendAddressPool": {
              "id": "/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Network/loadBalancers/{lbName}/backendAddressPools/backend-pool"
            },
            "probe": {
              "id": "/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Network/loadBalancers/{lbName}/probes/health-probe"
            },
            "protocol": "Tcp",
            "frontendPort": 80,
            "backendPort": 80
          }
        }
      ]
    }
  }' | python3 -m json.tool
```

### List Load Balancers

```bash
curl -s 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Network/loadBalancers?api-version=2024-01-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

## Network Interfaces

Provider: `Microsoft.Network/networkInterfaces`
api-version: `2024-01-01`

Required for VM creation. A NIC binds a VM to a subnet and optionally a public IP and NSG.

```bash
curl -s -X PUT 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Network/networkInterfaces/{nicName}?api-version=2024-01-01' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "eastus",
    "properties": {
      "ipConfigurations": [
        {
          "name": "ipconfig1",
          "properties": {
            "subnet": {
              "id": "/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Network/virtualNetworks/{vnetName}/subnets/{subnetName}"
            },
            "publicIPAddress": {
              "id": "/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Network/publicIPAddresses/{ipName}"
            }
          }
        }
      ],
      "networkSecurityGroup": {
        "id": "/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Network/networkSecurityGroups/{nsgName}"
      }
    }
  }' | python3 -m json.tool
```
