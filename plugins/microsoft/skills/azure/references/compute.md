# Compute Resources

Virtual machines, App Service, Functions, and container instances via Azure Resource Manager.

## Contents

- [Virtual Machines](#virtual-machines)
  - [List VMs](#list-vms)
  - [Get a VM](#get-a-vm)
  - [Create a VM](#create-a-vm)
  - [VM Power Operations](#vm-power-operations)
  - [Delete a VM](#delete-a-vm)
- [App Service (Web Apps)](#app-service-web-apps)
  - [List Web Apps](#list-web-apps)
  - [Get a Web App](#get-a-web-app)
  - [Create a Web App](#create-a-web-app)
  - [Restart a Web App](#restart-a-web-app)
  - [Deployment Slots](#deployment-slots)
- [Azure Functions](#azure-functions)
- [Container Instances](#container-instances)
  - [Create a Container Group](#create-a-container-group)
  - [List Container Groups](#list-container-groups)
  - [Get Container Logs](#get-container-logs)

## Virtual Machines

Provider: `Microsoft.Compute/virtualMachines`
api-version: `2024-03-01`

Base path:
```
/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines
```

### List VMs

```bash
curl -s 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines?api-version=2024-03-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

List all VMs in a subscription:
```bash
curl -s 'https://management.azure.com/subscriptions/{subId}/providers/Microsoft.Compute/virtualMachines?api-version=2024-03-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Get a VM

```bash
curl -s 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines/{vmName}?api-version=2024-03-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

Include instance view (power state, provisioning state):
```bash
curl -s 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines/{vmName}?$expand=instanceView&api-version=2024-03-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Create a VM

```bash
curl -s -X PUT 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines/{vmName}?api-version=2024-03-01' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "eastus",
    "properties": {
      "hardwareProfile": {
        "vmSize": "Standard_B2s"
      },
      "storageProfile": {
        "imageReference": {
          "publisher": "Canonical",
          "offer": "0001-com-ubuntu-server-jammy",
          "sku": "22_04-lts",
          "version": "latest"
        },
        "osDisk": {
          "createOption": "FromImage",
          "managedDisk": { "storageAccountType": "Standard_LRS" }
        }
      },
      "osProfile": {
        "computerName": "{vmName}",
        "adminUsername": "azureuser",
        "adminPassword": "REPLACE_WITH_SECURE_PASSWORD"
      },
      "networkProfile": {
        "networkInterfaces": [
          { "id": "/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Network/networkInterfaces/{nicName}" }
        ]
      }
    }
  }' | python3 -m json.tool
```

Required fields: `location`, `hardwareProfile`, `storageProfile`, `osProfile`, `networkProfile`.

A NIC must exist before creating the VM. See `storage-networking.md` for creating network resources.

### VM Power Operations

All power operations use POST and return 202 Accepted (async).

```bash
# Start
curl -s -X POST 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines/{vmName}/start?api-version=2024-03-01' \
  -H "Authorization: Bearer $TOKEN"

# Stop (power off — still incurs compute charges)
curl -s -X POST 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines/{vmName}/powerOff?api-version=2024-03-01' \
  -H "Authorization: Bearer $TOKEN"

# Deallocate (stop and release compute — no charges)
curl -s -X POST 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines/{vmName}/deallocate?api-version=2024-03-01' \
  -H "Authorization: Bearer $TOKEN"

# Restart
curl -s -X POST 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines/{vmName}/restart?api-version=2024-03-01' \
  -H "Authorization: Bearer $TOKEN"
```

### Delete a VM

```bash
curl -s -X DELETE 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines/{vmName}?api-version=2024-03-01' \
  -H "Authorization: Bearer $TOKEN"
```

Deleting a VM does **not** delete associated resources (NIC, disk, public IP). Delete those separately if needed.

## App Service (Web Apps)

Provider: `Microsoft.Web/sites`
api-version: `2023-12-01`

Base path:
```
/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Web/sites
```

### List Web Apps

```bash
curl -s 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Web/sites?api-version=2023-12-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Get a Web App

```bash
curl -s 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Web/sites/{appName}?api-version=2023-12-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Create a Web App

Requires an App Service Plan. Create the plan first:

```bash
curl -s -X PUT 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Web/serverfarms/{planName}?api-version=2023-12-01' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "eastus",
    "sku": { "name": "B1", "tier": "Basic" },
    "properties": {}
  }' | python3 -m json.tool
```

Then create the web app:

```bash
curl -s -X PUT 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Web/sites/{appName}?api-version=2023-12-01' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "eastus",
    "properties": {
      "serverFarmId": "/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Web/serverfarms/{planName}",
      "siteConfig": {
        "linuxFxVersion": "NODE|20-lts"
      }
    }
  }' | python3 -m json.tool
```

### Restart a Web App

```bash
curl -s -X POST 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Web/sites/{appName}/restart?api-version=2023-12-01' \
  -H "Authorization: Bearer $TOKEN"
```

### Deployment Slots

List slots:
```bash
curl -s 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Web/sites/{appName}/slots?api-version=2023-12-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

Swap slots:
```bash
curl -s -X POST 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Web/sites/{appName}/slotsswap?api-version=2023-12-01' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "targetSlot": "production",
    "preserveVnet": true
  }'
```

## Azure Functions

Functions use the same `Microsoft.Web/sites` provider as App Service with `kind: "functionapp"`.

```bash
curl -s -X PUT 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Web/sites/{funcAppName}?api-version=2023-12-01' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "kind": "functionapp",
    "location": "eastus",
    "properties": {
      "serverFarmId": "/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Web/serverfarms/{planName}",
      "siteConfig": {
        "appSettings": [
          { "name": "FUNCTIONS_WORKER_RUNTIME", "value": "node" },
          { "name": "FUNCTIONS_EXTENSION_VERSION", "value": "~4" },
          { "name": "AzureWebJobsStorage", "value": "{storageConnectionString}" }
        ]
      }
    }
  }' | python3 -m json.tool
```

Functions require a storage account connection string in `AzureWebJobsStorage`.

## Container Instances

Provider: `Microsoft.ContainerInstance/containerGroups`
api-version: `2023-05-01`

Base path:
```
/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.ContainerInstance/containerGroups
```

### Create a Container Group

```bash
curl -s -X PUT 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.ContainerInstance/containerGroups/{groupName}?api-version=2023-05-01' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "eastus",
    "properties": {
      "containers": [
        {
          "name": "my-container",
          "properties": {
            "image": "nginx:latest",
            "resources": {
              "requests": { "cpu": 1.0, "memoryInGB": 1.5 }
            },
            "ports": [{ "port": 80 }]
          }
        }
      ],
      "osType": "Linux",
      "ipAddress": {
        "type": "Public",
        "ports": [{ "protocol": "TCP", "port": 80 }]
      }
    }
  }' | python3 -m json.tool
```

### List Container Groups

```bash
curl -s 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.ContainerInstance/containerGroups?api-version=2023-05-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Get Container Logs

```bash
curl -s 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.ContainerInstance/containerGroups/{groupName}/containers/{containerName}/logs?api-version=2023-05-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

Add `&tail=100` to limit the number of log lines returned.
