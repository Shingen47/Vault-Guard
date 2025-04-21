import requests
import json

# Test the get-credentials-extension endpoint
def test_get_credentials():
    url = "http://127.0.0.1:5000/get-credentials-extension"
    headers = {"Content-Type": "application/json"}
    data = {"website": "facebook.com"}
    
    print(f"Sending request to {url} with data: {data}")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response data: {json.dumps(result, indent=2)}")
            
            if result.get("credentials"):
                print(f"Found {len(result['credentials'])} credentials")
                for cred in result["credentials"]:
                    print(f"Website: {cred.get('website')}, Username: {cred.get('username')}")
            else:
                print("No credentials found")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_get_credentials() 