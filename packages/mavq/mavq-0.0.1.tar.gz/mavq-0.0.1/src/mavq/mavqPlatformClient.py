import json
import requests
from commonProvider import URLENCODED_HEADER_ONLY
from mavqUserContext import MavQUserContext

"""
mavQ Platform client provide a support to login for your tenant user, and managing the
required configuration for client during the process.

@since 20-May-2022
@author Vishal Agarwal
@access public
"""
class mavqPlatformClient:

    """
    @param {Object} configuration - Configuration to init the MavQPlatformClient
    
    @example new MavQPlatformClient({
        tenant: 'system',
        coreApiBaseUrl: 'https://core.mavq.io',
        objectApiBaseUrl: 'https://objects.mavq.io',
        dataApiBaseUrl: 'https://data.mavq.io',
        authBaseUrl: 'https://auth.mavq.io',
        authClientId: 'login'
    })
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    """
    def __init__(self, tenant="invalid", coreApiBaseUrl="", objectApiBaseUrl="", dataApiBaseUrl="", authBaseUrl="", authClientId=""):
        self.tenant = tenant
        self.coreApiBaseUrl = coreApiBaseUrl
        self.objectApiBaseUrl = objectApiBaseUrl
        self.dataApiBaseUrl = dataApiBaseUrl
        self.authBaseUrl = authBaseUrl
        self.authClientId = authClientId

        """
        private variables specific to client
        """
        self.__DEFAULT_TENANT_NAME = "invalid"
        self.__DEFAULT_VALUE_TO_VALIDATE = [None, '']
        self.__GRANT_TYPE = 'password'
        self.__AUTH_SCOPE = 'openid'
        self.__access_token = None
    
    def version(self):
        return "0.0.1"

    """
    Validate the configuration for mavQPlatfomClient
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access private
    
    return String[] - If Any field does not contain valid value
    """
    def validateConfiguration(self):
        invalidFields = []
        if(self.tenant in [self.__DEFAULT_TENANT_NAME] or self.tenant in self.__DEFAULT_VALUE_TO_VALIDATE):
            invalidFields.append('tenant')
        if(self.coreApiBaseUrl in self.__DEFAULT_VALUE_TO_VALIDATE):
            invalidFields.append('coreApiBaseUrl')
        if(self.objectApiBaseUrl in self.__DEFAULT_VALUE_TO_VALIDATE):
            invalidFields.append('objectApiBaseUrl')
        if(self.dataApiBaseUrl in self.__DEFAULT_VALUE_TO_VALIDATE):
            invalidFields.append('dataApiBaseUrl')
        if(self.authBaseUrl in self.__DEFAULT_VALUE_TO_VALIDATE):
            invalidFields.append('authBaseUrl')
        if(self.authClientId in self.__DEFAULT_VALUE_TO_VALIDATE):
            invalidFields.append('authClientId')
        return invalidFields
    
    """
    Login and provide the user context for given tenant
    
    @param {String} userResourceUri - User resource uri
    @param {String} password - Password
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    return mavQUserContext - Return the mavQ User context
    """
    def loginAndGetUserContext(self, userResourceUri="", password=""):
        self.loginAndGetTokenOnly(userResourceUri, password)
        return MavQUserContext(self.__access_token, userResourceUri, password)
    
    """
    Login and provide the access token for given user
    
    @param {String} userResourceUri - User resource uri
    @param {String} password - Password
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    return {String} - Return the keycloak access token
    """
    def loginAndGetTokenOnly(self, userResourceUri="", password=""):
        
        invalidFields = self.validateConfiguration()
        if(invalidFields and len(invalidFields)):
            raise Exception("Missing or invalidate the required configuration properties {invalidFields}".format(invalidFields=", ".join(invalidFields)))
        
        params = {
            "client_id": self.authClientId,
            "username": userResourceUri,
            "password": password,
            "grant_type": self.__GRANT_TYPE
        }

        reqUrl = self.authBaseUrl + "/auth/realms/platform-auth-dev/protocol/openid-connect/token"

        response = requests.post(reqUrl, data=params, headers=URLENCODED_HEADER_ONLY)
        self.__access_token = json.loads(response.content)["access_token"]

        return response.content

    """
    Provide a request url of appropriate service of mavQ Platform
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access private
    
    @return {String} Return the service url for search operation on tenant and resource kind
    """
    def __getRequestUrl(self, service="", version=1, tenant="", operation="search/"):
        serviceUrl = ""
        if(service == "CORE"):
            serviceUrl = self.coreApiBaseUrl
        elif(service == "OBJECT"):
            serviceUrl = self.objectApiBaseUrl
        elif(service == "DATA"):
            serviceUrl = self.dataApiBaseUrl
        elif(service == "AUTH"):
            serviceUrl = self.authBaseUrl
        else:
            raise Exception("Invalid service request")
        reqUrl = serviceUrl + "/v{version}/tenants/{tenant}/{operation}".format(version=str(version), tenant=tenant, operation=operation)
        return reqUrl

    """
    Provide a List of Object fields for objectConfigurationUri
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    @return {JSON} Return the ObjectFields for objectConfigurationUri
    """
    def getObjectFields(self, searchQuery, searchId="search"):
        return self.__request("OBJECT", 1, "POST", searchQuery, ["object_fields", searchId])
    
    """
    Operation to create Object Field
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    @return {JSON} Return the ObjectField (created)
    """
    def createObjectField(self, body):
        return self.__request("OBJECT", 1, "POST", body, ["object_fields"])
    
    """
    Operation to update Object Field
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    @return {JSON} Return the ObjectField (updated)
    """
    def updateObjectField(self, body, fieldId):
        return self.__request("OBJECT", 1, "PUT", body, ["object_fields", fieldId])
    
    """
    Operation to delete Object Field
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    @return Status for deletion
    """
    def deleteObjectField(self, fieldId):
        return self.__request("OBJECT", 1, "DELETE", None, ["object_fields", fieldId])
    
    """
    Provide a List of Object Layouts for objectConfigurationUri
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    @return {JSON} Return the ObjectLayouts for objectConfigurationUri
    """
    def getObjectLayouts(self, searchQuery):
        return self.__request("OBJECT", 2, "POST", searchQuery, ["object_layouts"])
    
    """
    Operation to create Object Layout
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    @return {JSON} Return the ObjectLayout (created)
    """
    def createObjectLayout(self, body):
        return self.__request("OBJECT", 2, "POST", body, ["object_layouts"])
    
    """
    Operation to update Object Layout
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    @return {JSON} Return the ObjectLayout (updated)
    """
    def updateObjectLayout(self, body, layoutId):
        return self.__request("OBJECT", 2, "PUT", body, ["object_layouts", layoutId])

    """
    Provide a List of Object Record Types for objectConfigurationUri
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    @return {JSON} Return the ObjectRecordTypes for objectConfigurationUri
    """
    def getObjectRecordTypes(self, searchQuery, searchId="search"):
        if(searchId == "POST"):
            return self.__request("OBJECT", 1, "POST", searchQuery, ["object_record_types", searchId])
        return self.__request("OBJECT", 1, "GET", searchQuery, ["object_record_types", searchId])

    """
    Operation to create Object Layout
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    @return {JSON} Return the ObjectLayout (created)
    """
    def createObjectRecordType(self, body):
        return self.__request("OBJECT", 1, "POST", body, ["object_record_types"])
    
    """
    Operation to update Object Layout
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    @return {JSON} Return the ObjectLayout (updated)
    """
    def updateObjectRecordType(self, body, recordTypeId):
        return self.__request("OBJECT", 1, "PUT", body, ["object_record_types", recordTypeId])
    
    """
    Provide a List of Objects
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    @return {JSON} Return the Objects
    """
    def getObjects(self, searchQuery, objectName="search"):
        return self.__request("OBJECT", 1, "GET", searchQuery, ["object_configurations", objectName])
    
    """
    Operation to create record
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    @return {JSON} Return the created Object Record
    """
    def createObject(self, body):
        return self.__request("OBJECT", 1, "POST", body, ["operations"])
    
    """
    Operation to update record
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    @return {JSON} Return the updated Object Record
    """
    def updateObject(self, body, objectId):
        return self.__request("OBJECT", 1, "PUT", body, ["object_configurations", objectId])
    
    """
    Operation to delete record
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    @return confirmation status for operation
    """
    def deleteObject(self, objectId):
        return self.__request("OBJECT", 1, "DELETE", None, ["object_configurations", objectId])

    """
    Provide a List of Object Records with provided search request
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    @return {JSON} Return the Object Records
    """
    def searchObjectRecords(self, oqlQuery, searchId):
        return self.__request("OBJECT", 2, "POST", oqlQuery, ["object_manager", "sql", searchId])
    
    """
    Operation to create record
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    @return {JSON} Return the created Object Record
    """
    def createObjectRecord(self, body, objectName):
        return self.__request("OBJECT", 2, "POST", body, ["object_manager", "sql", objectName])
    
    """
    Operation to update record
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    @return {JSON} Return the updated Object Record
    """
    def updateObjectRecord(self, body, objectName, recordId):
        return self.__request("OBJECT", 2, "PUT", body, ["object_manager", "sql", objectName, recordId])
    
    """
    Operation to delete record
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    @return confirmation status for operation
    """
    def deleteObjectRecord(self, objectName, recordId):
        return self.__request("OBJECT", 2, "DELETE", None, ["object_manager", "sql", objectName, recordId])

    """
    Operation to request BE Server
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access private
    
    @return {JSON} BE response as per request type
    """
    def __request(self, resourceType, apiVersion, requestType, bodyParams, queryParams):
        invalidFields = self.validateConfiguration()
        if(invalidFields and len(invalidFields)):
            raise Exception("Missing or invalidate the required configuration properties {invalidFields}".format(invalidFields=", ".join(invalidFields)))
        
        access_token = self.get_access_token()
        headers = {"Authorization": "Bearer {}".format(access_token), "Content-Type": "application/json"}

        queryParam =  "/".join([("" if x is None else x) for x in queryParams])
        reqUrl = self.__getRequestUrl(resourceType, apiVersion, self.tenant, queryParam) + "/"

        if(requestType == "POST"):
            return requests.post(reqUrl, json=bodyParams, headers=headers)
        elif(requestType == "PUT"):
            return requests.put(reqUrl, json=bodyParams, headers=headers)
        elif(requestType == "DELETE"):
            return requests.delete(reqUrl, headers=headers)
        elif(requestType == "GET"):
            return requests.get(reqUrl, headers=headers)
        else:
            raise Exception("Unknown request type")


    def get_access_token(self):
        return self.__access_token
        
    
    """
    Provide a service url of core service of mavQ Platform
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    @return {String} Return the core service url
    """
    def getCoreServiceBaseUrl(self):
        return self.coreApiBaseUrl

    """
    Provide a service url of data service of mavQ Platform
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    @return {String} Return the data service url
    """
    def getDataServiceBaseUrl(self):
        return self.dataApiBaseUrl

    """
    Provide a service url of objects service of mavQ Platform
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    @return {String} Return the objects service url
    """
    def getObjectServiceBaseUrl(self):
        return self.objectApiBaseUrl
    
    """
    Provide a service url of Keycloak service of mavQ Platform
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    @return {String} Return the Keycloak service url
    """
    def getAuthBaseUrl(self):
        return self.authBaseUrl
    
    """
    Provide a configured tenant name
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    @return {String} Return the configured tenant name
    """
    def getTenantName(self):
        return self.tenant
    