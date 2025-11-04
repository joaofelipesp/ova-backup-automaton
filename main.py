from datetime import datetime
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

baseUrl = "https://172.17.200.70:9440/api/nutanix/v3"

listVmsUrl = baseUrl+"/vms/list"

listVmsPayload =  """{
	"kind": "vm",
	"length": 200,
	"offset": 0
}"""

# Usado para ordenar a lista de VMs por nome
def vmListSort(n):
	return str.lower(n['name'])

def getExportVmUrl(uuid: str):
	return f"{baseUrl}/vms/{uuid}/export"

def getExportVmPayload(vmName: str):
	now = datetime.now()
	today = now.strftime("__%d_%m_%Y")
	return json.dumps({"name": vmName + today, "disk_file_format": "vmdk"})

# Retorna um header de requisição HTTP para usar nas chamadas de API 
def getHeader(token: str, reqType="POST"):
	hdr = {
		"Accept": "application/json",
		"Authorization": f"Basic {token}"
	}
	if(reqType == "POST"): hdr.update({"Content-Type": "application/json"})

	return hdr

# Cria um arquivo next_vms_list.txt com os nomes e UUID das VMs
def getVmList():
	with open("api_basic_auth_token.txt", 'r') as f:
		token = f.read().strip()

	response = requests.request("POST", listVmsUrl, data=listVmsPayload, headers=getHeader(token), verify=False)
	if(response.status_code != 200):
		print(f"Error: API returned status code {response.status_code}")
		print(response.text)
		exit(1)
	
	vmListRaw = json.loads(response.text)
	vmList = []

	for vm in vmListRaw["entities"]:
		try:
			uuid = vm['metadata']['uuid']
			name = vm['status']['name']
			vmList.append({"uuid": uuid, "name": name})
		except KeyError as e:
			print(f"Warning: Skipping VM due to missing key: {e}")
	
	vmList.sort(key = vmListSort)
	
	with open("next_vms_list.txt", "a") as f:
		for vm in vmList:
			f.write(f"{vm["uuid"]},{vm["name"]}\n")

def main():
	getVmList()

if __name__ == "__main__":
	main()